import asyncio

from aiogram import types, Router

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from configs.config import lobbies
from configs.config import lobby_to_user_id
from configs.config import player_stats
from configs.player import Player
from StateGroup.game_states import game_states
from keyboards.start_game_keyboard import start_game_keyboard
from configs.utils import send_mess

router = Router()




@router.message(game_states.in_lobby)
async def send_message(message: types.Message) -> None:
    game_id = lobby_to_user_id.get(message.from_user.id)
    if game_id is not None:
        await send_mess(message,game_id)
    else:
        await message.bot.send_message(message.from_user.id, "Game ID not found")
    if message.from_user.id == lobbies[game_id].host and lobbies[game_id].state == game_states.in_lobby:
        await message.bot.send_message(lobbies[game_id].host, "Чтобы начать игру нажмите на кнопку: ",
                                       reply_markup=start_game_keyboard())


@router.message(game_states.in_lobby)
@router.callback_query(lambda query: query.data == "/start")
async def start_game(query: types.CallbackQuery, state: FSMContext):
    await query.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    game_id = lobby_to_user_id.get(query.from_user.id)
    lobbies[game_id].set_state(game_states.in_game)
    lobbies[game_id].round += 1
    lobbies[game_id].set_game_id(game_id)
    for player_id in lobbies[game_id].players:
        player_key = StorageKey(bot_id=query.bot.id, user_id=player_id,chat_id=player_id)
        player_context = FSMContext(key=player_key, storage=state.storage)
        player_stats[player_id] = Player(game_id)
        player = player_stats.get(player_id)
        await player_context.set_state(game_states.in_game)
        await query.message.bot.send_message(player_id, f"Игра {game_id} началась!")
        await query.message.bot.send_message(player_id, "Введите сообщение чтобы начать игру")
        await query.message.bot.send_message(player_id, f"Ваши характеристики:\n {player.show_cards()}")

