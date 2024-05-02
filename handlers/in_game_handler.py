import asyncio
import re


from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey


from configs.config import lobbies
from configs.config import lobby_to_user_id
from configs.config import id_to_nick
from keyboards import choice_card
from keyboards.vote_keyboard import kick_keyboard
from StateGroup.game_states import game_states
from configs.utils import send_mess,show_chosen_card, round_message
from handlers.vote_for_kick_handler import get_most_voted_player

router = Router()

@router.message(game_states.in_game)
async def round_progress(message: types.Message, state: FSMContext):
    game_id = lobby_to_user_id.get(message.from_user.id)
    current_lobby = lobbies[game_id]
    if get_most_voted_player(current_lobby.votes_for_players) is not None:
        kicked_player = get_most_voted_player(current_lobby.votes_for_players)
        current_lobby.reset_votes_for_kick()
        await round_message(message, f"Игрок {kicked_player} изгнан!", game_id)
        kicked_player = find_id_by_nick(kicked_player)
        current_lobby.players.remove(kicked_player)
        current_lobby.player_stats.pop(kicked_player)
        kicked_key = StorageKey(bot_id=message.bot.id, user_id=kicked_player,chat_id=kicked_player)
        kicked_contex = FSMContext(key=kicked_key, storage=state.storage)
        await kicked_contex.set_state(None)
        if len(current_lobby.players) == 0:
            del lobbies[game_id]
    if (current_lobby.get_round() > 6):
        await round_message(message,"Игра окончена!",game_id)
    else:
        if current_lobby.get_state() != game_states.in_game_speaker:
            current_lobby.set_speaker(current_lobby.players[current_lobby.get_speaker_index()])
        if message.from_user.id == current_lobby.get_speaker():
            speaker = current_lobby.get_speaker()
            speaker_key = StorageKey(bot_id=message.bot.id, user_id=speaker, chat_id=speaker)
            speaker_context = FSMContext(key=speaker_key, storage=state.storage)
            current_lobby.set_state(game_states.in_game_speaker)
            await speaker_context.set_state(game_states.choice_card_to_show)
            await message.bot.send_message(speaker, "Выберите карту для открытия",
                                           reply_markup=choice_card.choice_card_keyboard(current_lobby.get_player_stats(speaker)))
        else:
            await message.answer("Сейчас говорит другой игрок")

@router.message(game_states.choice_card_to_show)
@router.callback_query(lambda query: re.match(r"card_\w+",query.data))
async def chosen_card(query: types.CallbackQuery, state: FSMContext):
    game_id = lobby_to_user_id.get(query.from_user.id)
    current_lobby = lobbies[game_id]
    speaker = current_lobby.get_speaker()
    speaker_name = query.from_user.username or query.from_user.first_name
    speaker_key = StorageKey(bot_id=query.bot.id, user_id=speaker, chat_id=speaker)
    speaker_context = FSMContext(key=speaker_key, storage=state.storage)
    player = current_lobby.get_player_stats(speaker)
    card_to_show = query.data.split("_")[1]
    if (card_to_show in player.shown_cards):
        await query.message.bot.send_message(speaker, "Вы уже показывали эту карту")
        await speaker_context.set_state(game_states.choice_card_to_show)
    elif (card_to_show != player.profession and current_lobby.get_round() == 1):
        await query.message.bot.send_message(speaker, "На первом раунде можно показывать только карту профессии!")
        await speaker_context.set_state(game_states.choice_card_to_show)
    else:
        await show_chosen_card(query.message, game_id, card_to_show, speaker_name)
        try:
            await query.message.bot.send_message(speaker, "Ваша очередь говорить. У вас есть 30 сек.")
        except Exception as e:
            print(f"Failed to send message: {str(e)}")
        player.add_shown_card(card_to_show)
        await speaker_context.set_state(game_states.in_game_speaker)


@router.message(game_states.in_game_speaker)
async def speak(message: types.Message, state: FSMContext):
    game_id = lobby_to_user_id.get(message.from_user.id)
    current_lobby = lobbies[game_id]
    speaker = message.from_user.id

    # Ensure each speaker has a unique timer_key
    timer_key = f"timer_{speaker}"
    timer_started = await state.get_data()
    timer_started = timer_started.get(timer_key, False)
    await send_mess(message, game_id)
    # Start the timer when the first message from the speaker is detected
    if not timer_started:
        await state.update_data({timer_key: True})
        timer_task = asyncio.create_task(timer(state))  # Timer set for 30 seconds
        await timer_task
        # Handling timer completion
        if timer_task.done():
            try:
                current_lobby.next_speaker_index()
                current_lobby.set_state(game_states.in_game)
                speaker_index = current_lobby.get_speaker_index()
                next_speaker = id_to_nick.get(current_lobby.players[speaker_index])
                await round_message(message,f"Время вышло! Следующий: {next_speaker}", game_id)
            except IndexError:
                current_lobby.next_round()
                current_lobby.reset_speaker_index()
                await round_message(message, "Все игроки сказали свое слово! Голосование за исключение!", game_id)
                for player_id in current_lobby.players:
                    player_key = StorageKey(bot_id=message.bot.id, user_id=player_id, chat_id=player_id)
                    player_context = FSMContext(key=player_key, storage=state.storage)
                    await message.bot.send_message(player_id, "Выберите кого хотите изгнать?",
                                                   reply_markup=kick_keyboard(current_lobby))
                    await player_context.set_state(game_states.vote_for_kick)
            # Reset the timer state for the next message
            finally:
                await state.update_data({timer_key: False})
                await state.set_state(game_states.in_game)


async def timer(state: FSMContext, duration=3):
    await asyncio.sleep(duration)

def find_id_by_nick(username):
    for key in id_to_nick:
        if id_to_nick[key] == username:
            return key

