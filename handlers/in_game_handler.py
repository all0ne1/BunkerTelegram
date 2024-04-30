import asyncio
import re
import time
from datetime import datetime

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.filters import Command
from aiogram.types import ChatPermissions

from configs.config import lobbies
from configs.config import lobby_to_user_id
from configs.config import player_stats, id_to_nick
from keyboards import choice_card
from keyboards.start_game_keyboard import start_game_keyboard
from StateGroup.game_states import game_states
from configs.utils import send_mess,show_chosen_card, round_message

router = Router()

@router.message(game_states.in_game)
async def round_progress(message: types.Message, state: FSMContext):
    game_id = lobby_to_user_id.get(message.from_user.id)
    current_lobby = lobbies[game_id]
    if current_lobby.get_speaker_index() >= len(current_lobby.players):
        await round_message(message,"Все игроки сказали свое слово! Следующий раунд",game_id)
    if current_lobby.get_state() != game_states.in_game_speaker:
        current_lobby.set_speaker(current_lobby.players[current_lobby.get_speaker_index()])
    if message.from_user.id == current_lobby.get_speaker():
        speaker = current_lobby.get_speaker()
        speaker_key = StorageKey(bot_id=message.bot.id, user_id=speaker, chat_id=speaker)
        speaker_context = FSMContext(key=speaker_key, storage=state.storage)
        current_lobby.set_state(game_states.in_game_speaker)
        await speaker_context.set_state(game_states.choice_card_to_show)
        await message.bot.send_message(speaker, "Выберите карту для открытия",
                                       reply_markup=choice_card.choice_card_keyboard(player_stats.get(speaker)))
    else:
        await message.answer("Сейчас говорит другой игрок")

@router.message(game_states.choice_card_to_show)
@router.callback_query(lambda query: re.match(r"\w+",query.data))
async def chosen_card(query: types.CallbackQuery, state: FSMContext):
    game_id = lobby_to_user_id.get(query.from_user.id)
    current_lobby = lobbies[game_id]
    card_to_show = query.data
    speaker = current_lobby.get_speaker()
    speaker_name = query.from_user.username or query.from_user.first_name
    speaker_key = StorageKey(bot_id=query.message.bot.id, user_id=speaker, chat_id=speaker)
    speaker_context = FSMContext(key=speaker_key, storage=state.storage)
    await show_chosen_card(query.message,game_id,card_to_show,speaker_name)
    try:
        await query.message.bot.send_message(speaker, "Ваша очередь говорить. У вас есть 30 сек.")
    except Exception as e:
        print(f"Failed to send message: {str(e)}")
        print(current_lobby.get_speaker())
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
                await round_message(message,"Все игроки сказали свое слово! Следующий раунд",game_id)

            # Reset the timer state for the next message
            await state.update_data({timer_key: False})
            await state.set_state(game_states.in_game)



async def timer(state: FSMContext, duration=30):
    await asyncio.sleep(duration)

