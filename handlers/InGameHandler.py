from aiogram import types, Router, F

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from configs.config import lobbies
from configs.config import lobby_to_user_id
from StateGroup.JoinGame import JoinGame
from aiogram.utils.markdown import hbold
from keyboards.start_menu import build_start_keyboard
from keyboards.start_game_keyboard import start_game_keyboard

router = Router()


@router.message(Command('exit'))
async def exit_game(message: types.Message, state: FSMContext):
    exit_player_name = message.from_user.username or message.from_user.first_name
    game_id = lobby_to_user_id.get(message.from_user.id)
    for player_id in lobbies[game_id].players:
        if player_id != message.from_user.id:
            try:
                player = await message.bot.get_chat(player_id)
                await message.bot.send_message(player.id, f'Игрок {exit_player_name} покинул игру!')
            except Exception as e:
                print(f"Ошибка при отправке сообщения игроку {player_id}: {e}")
        else:
            await message.bot.send_message(player_id,f"Вы покинули игру {game_id}")
    lobbies[game_id].players.remove(message.from_user.id)
    if len(lobbies[game_id].players) == 0:
        del lobbies[game_id]
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!", reply_markup=build_start_keyboard())
    await state.set_state(None)


@router.message(JoinGame.joined or JoinGame.in_game)
async def send_message(message: types.Message) -> None:
    game_id = lobby_to_user_id.get(message.from_user.id)
    if game_id is not None:
        sender_name = message.from_user.username or message.from_user.first_name
        for player_id in lobbies[game_id].players:
            if player_id != message.from_user.id:
                try:
                    await message.bot.send_message(player_id, f"Игрок {sender_name} написал: {message.text}")
                except Exception as e:
                    print(f"Error sending message to {player_id}: {e}")
    else:
        await message.bot.send_message(message.from_user.id, "Game ID not found")
    if message.from_user.id == lobbies[game_id].host and lobbies[game_id].state == JoinGame.joined:
        await message.bot.send_message(lobbies[game_id].host, "Чтобы начать игру нажмите на кнопку: ",
                                       reply_markup=start_game_keyboard())


@router.message(JoinGame.joined)
@router.callback_query(lambda query: query.data == "/start")
async def start_game(query: types.CallbackQuery, state: FSMContext):
    game_id = lobby_to_user_id.get(query.from_user.id)
    print(game_id)
    lobbies[game_id].set_state(JoinGame.in_game)
    for player_id in lobbies[game_id].players:
        user_state = FSMContext(state.storage, player_id)
        lobbies[game_id].round += 1
        await user_state.update_data(state=JoinGame.in_game)
        await query.message.bot.send_message(player_id,f"Игра {game_id} началась!")

