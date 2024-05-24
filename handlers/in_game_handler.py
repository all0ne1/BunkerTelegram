import asyncio
import re


from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey


from configs.config import lobbies
from configs.config import lobby_by_user_id
from configs.config import id_to_nick
from keyboards.choice_card import choice_card_keyboard
from keyboards.vote_keyboard import kick_keyboard
from StateGroup.gamestates import GameStates
from configs.utils import send_mess, show_chosen_card, round_message, change_every_player_state, change_one_player_state


router = Router()


@router.message(GameStates.in_game)
async def round_progress(message: types.Message, state: FSMContext):
    game_id = lobby_by_user_id.get(message.from_user.id)
    current_lobby = lobbies[game_id]
    if len(current_lobby.players) == current_lobby.players_for_game_over:
        await round_message(message, f"Игра окончена! Выжившие: {current_lobby.print_survivors()}", game_id)
        await change_every_player_state(game_id, state, None)
        return

    if current_lobby is None:
        await message.answer("Лобби не найдено.")
        return

    if len(current_lobby.players) == 0:
        del lobbies[game_id]
        await message.answer("Все игроки покинули лобби. Игра окончена!")
        return

    if current_lobby.get_state() == GameStates.revote:
        await message.answer("Дождитесь переголосования")
        return

    if (not current_lobby.bunker_stat_revealed and current_lobby.bunker_stats and
            current_lobby.get_state() == GameStates.in_game):
        current_lobby.bunker_stat_revealed = True
        await round_message(message, f"Новая информация о бункере: \n{current_lobby.get_one_bunker_stat()}", game_id)

    if current_lobby.get_state() != GameStates.in_game_speaker:
        current_lobby.set_speaker(current_lobby.players[current_lobby.get_speaker_index()])
    if message.from_user.id == current_lobby.get_speaker():
        speaker = current_lobby.get_speaker()
        current_lobby.set_state(GameStates.in_game_speaker)
        await message.bot.send_message(speaker, "Выберите карту для открытия",
                                       reply_markup=choice_card_keyboard(
                                           current_lobby.get_player_stats(speaker)))
        await change_one_player_state(speaker, state, GameStates.choice_card_to_show)
    else:
        await message.answer("Сейчас говорит другой игрок")


@router.message(GameStates.choice_card_to_show)
async def choice_card_echo_handler(message: types.Message):
    await message.bot.send_message(message.from_user.id, "Выбери карту, которую хотите открыть")


@router.message(GameStates.choice_card_to_show)
@router.callback_query(lambda query: re.match(r"card_\w+", query.data))
async def chosen_card(query: types.CallbackQuery, state: FSMContext):
    game_id = lobby_by_user_id.get(query.from_user.id)
    current_lobby = lobbies[game_id]
    speaker = current_lobby.get_speaker()
    speaker_name = query.from_user.username or query.from_user.first_name
    player = current_lobby.get_player_stats(speaker)
    card_to_show = query.data.split("_")[1]
    if card_to_show in player.shown_cards:
        await query.message.bot.send_message(speaker, "Вы уже показывали эту карту")
    elif card_to_show != player.profession and current_lobby.get_round() == 1:
        await query.message.bot.send_message(speaker, "На первом раунде можно показывать только карту профессии!")
    else:
        await show_chosen_card(query.message, game_id, card_to_show, speaker_name)
        try:
            await query.message.bot.send_message(speaker, "Ваша очередь говорить. У вас есть 30 сек.")
        except Exception as e:
            print(f"Failed to send message: {str(e)}")
        player.add_shown_card(card_to_show)
        await change_one_player_state(speaker, state, GameStates.in_game_speaker)


@router.message(GameStates.in_game_speaker)
async def speak(message: types.Message, state: FSMContext):
    game_id = lobby_by_user_id.get(message.from_user.id)
    current_lobby = lobbies[game_id]
    speaker = message.from_user.id
    timer_key = f"timer_{speaker}"
    timer_started = await state.get_data()
    timer_started = timer_started.get(timer_key, False)
    await send_mess(message, game_id)
    if not timer_started:
        await state.update_data({timer_key: True})
        timer_task = asyncio.create_task(timer())
        await timer_task
        if timer_task.done():
            try:
                current_lobby.next_speaker_index()
                current_lobby.set_state(GameStates.in_game)
                speaker_index = current_lobby.get_speaker_index()
                next_speaker_id = current_lobby.players[speaker_index]
                current_lobby.set_speaker(next_speaker_id)
                next_speaker_name = id_to_nick.get(next_speaker_id)
                await round_message(message, f"Время вышло! Следующий: {next_speaker_name}", game_id)
                await message.bot.send_message(next_speaker_id, "Выберите карту для открытия",
                                               reply_markup=choice_card_keyboard(
                                                   current_lobby.get_player_stats(next_speaker_id)))
                await change_one_player_state(next_speaker_id, state, GameStates.choice_card_to_show)
            except IndexError:
                current_lobby.next_round()
                current_lobby.reset_speaker_index()
                await round_message(message, "Все игроки сказали свое слово! Голосование за исключение!", game_id)
                for player_id in current_lobby.players:
                    player_key = StorageKey(bot_id=message.bot.id, user_id=player_id, chat_id=player_id)
                    player_context = FSMContext(key=player_key, storage=state.storage)
                    await message.bot.send_message(player_id, "Выберите кого хотите изгнать",
                                                   reply_markup=kick_keyboard(current_lobby))
                    await player_context.set_state(GameStates.vote_for_kick)
            finally:
                await state.update_data({timer_key: False})
                await state.set_state(GameStates.in_game)


async def timer(duration=1):
    await asyncio.sleep(duration)


def find_id_by_nick(username):
    for key in id_to_nick:
        if id_to_nick[key] == username:
            return key
