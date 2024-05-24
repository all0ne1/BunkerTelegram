from aiogram import types, Router

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import CallbackQuery

from configs.config import lobbies
from configs.config import lobby_by_user_id
from StateGroup.gamestates import GameStates
from keyboards.start_game_keyboard import start_game_keyboard
from configs.utils import send_mess

router = Router()


@router.message(GameStates.in_lobby)
async def send_message(message: types.Message) -> None:
    game_id = lobby_by_user_id.get(message.from_user.id)
    if game_id is not None:
        await send_mess(message, game_id)
    else:
        await message.bot.send_message(message.from_user.id, "Game ID not found")
    if message.from_user.id == lobbies[game_id].host and lobbies[game_id].state == GameStates.in_lobby:
        await message.bot.send_message(lobbies[game_id].host, "Чтобы начать игру нажмите на кнопку: ",
                                       reply_markup=start_game_keyboard())


@router.message(GameStates.in_lobby)
@router.callback_query(lambda query: query.data == "/start")
async def start_game(query: types.CallbackQuery, state: FSMContext):
    game_id = lobby_by_user_id.get(query.from_user.id)
    current_lobby = lobbies[game_id]
    if False:
        await query.bot.send_message(query.from_user.id, "Для начала игры необходимо минимум 4 игрока")
    else:
        await query.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
        current_lobby.set_state(GameStates.in_game)
        current_lobby.round += 1
        current_lobby.set_game_id(game_id)
        current_lobby.set_players_for_game_over(len(current_lobby.players) // 2)
        for player_id in lobbies[game_id].players:
            player_key = StorageKey(bot_id=query.bot.id, user_id=player_id, chat_id=player_id)
            player_context = FSMContext(key=player_key, storage=state.storage)
            lobbies[game_id].add_player_stats(player_id)
            player = lobbies[game_id].player_stats.get(player_id)
            await player_context.set_state(GameStates.in_game)
            await query.message.bot.send_message(player_id, f"Игра {game_id} началась!")
            await query.message.bot.send_message(player_id, f"Происшествие: {current_lobby.get_cataclysm()}")
            await query.message.bot.send_message(player_id, f"Ваши характеристики:\n {player.show_cards()}")
            await query.message.bot.send_message(player_id, "Введите сообщение чтобы начать игру")


@router.message(GameStates.in_lobby)
@router.callback_query(lambda query: query.data == "/share")
async def share(query: CallbackQuery):
    game_id = lobby_by_user_id.get(query.from_user.id)
    host_id = lobbies[game_id].get_host()
    await query.message.bot.send_message(host_id, f"https://t.me/ProjectBunketBot?start=join_lobby_{game_id}")
