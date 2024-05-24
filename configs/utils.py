import re

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from configs.config import bot_id

from configs.config import lobbies


async def send_mess(message, game_id):
    sender_name = message.from_user.username or message.from_user.first_name
    for player_id in lobbies[game_id].players:
        if player_id != message.from_user.id:
            try:
                await message.bot.send_message(player_id, f"Игрок {sender_name} написал: {message.text}")
            except Exception as e:
                print(f"Error sending message to {player_id}: {e}")


async def round_message(message, text, game_id, reply_markup=None):
    for player_id in lobbies[game_id].players:
        try:
            await message.bot.send_message(player_id, text, reply_markup=reply_markup)
        except Exception as e:
            print(f"Error sending message to {player_id}: {e}")


def get_id_by_nickname(nickname, user_dict):
    for user_id, user_nickname in user_dict.items():
        if user_nickname == nickname:
            return user_id
    return None


async def show_chosen_card(message, game_id, game_card, sender):
    sender_name = sender
    for player_id in lobbies[game_id].players:
        if player_id != message.from_user.id:
            try:
                await message.bot.send_message(player_id, f"Игрок {sender_name} выбрал карту: {game_card}")
            except Exception as e:
                print(f"Error sending message to {player_id}: {e}")


async def change_every_player_state(game_id, state: FSMContext, state_name):
    for player_id in lobbies[game_id].players:
        player_key = StorageKey(bot_id=bot_id, user_id=player_id, chat_id=player_id)
        player_context = FSMContext(key=player_key, storage=state.storage)
        await player_context.set_state(state_name)


async def change_one_player_state(player_id, state: FSMContext, state_name):
    player_key = StorageKey(bot_id=bot_id, user_id=player_id, chat_id=player_id)
    player_context = FSMContext(key=player_key, storage=state.storage)
    await player_context.set_state(state_name)


def remove_spec_characters(text):
    text = text.replace('\r', ' ').replace('\n', ' ')
    text = re.sub(r'[^a-zA-Zа-яА-Я0-9\s]', '', text)
    return text
