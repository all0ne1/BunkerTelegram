import random
from aiogram import types, Router

from aiogram.fsm.context import FSMContext
from configs.config import lobbies
from StateGroup.JoinGame import JoinGame
from configs.config import lobby_to_user_id
from aiogram.utils.markdown import hbold
from keyboards.start_menu import build_start_keyboard

router = Router()



@router.callback_query(lambda query: query.data == "/create")
async def create_callback_handler(query: types.CallbackQuery, state: FSMContext) -> None:
    await query.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    game_id = generate_game_id()
    lobbies[game_id].add_player(query.from_user.id)
    lobbies[game_id].game_id = game_id
    lobby_to_user_id[query.from_user.id] = game_id
    await query.message.answer(f"Игра создана! ID игры: {game_id}")
    await state.set_state(JoinGame.join)


@router.callback_query(lambda query: query.data == "/join")
async def join_callback_handler(query: types.CallbackQuery, state: FSMContext) -> None:
    await query.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    if await state.get_state() != JoinGame.join:
        await query.message.answer("Введите ID игры, к который в хотите присоединиться")
        await state.set_state(JoinGame.waiting_for_game_id)
    else:
        await query.message.answer(f"Вы уже находитель в игре {lobby_to_user_id.get(query.from_user.id)}")
        await state.set_state(JoinGame.join)


@router.message(JoinGame.waiting_for_game_id)
async def process_join(message: types.Message, state: FSMContext) -> None:
    if (message.text == "/exit"):
        await message.answer("Вы вышли в меню")
        await message.answer(f"Hello, {hbold(message.from_user.full_name)}!", reply_markup=build_start_keyboard())
        await state.set_state(None)
        return
    try:
        game_id = int(message.text)
        if game_id in lobbies:
            new_player_name = message.from_user.username or message.from_user.first_name
            lobbies[game_id].add_player(message.from_user.id)
            lobby_to_user_id[message.from_user.id] = game_id
            for player_id in lobbies[game_id].players:
                if player_id != message.from_user.id:  # Не отправлять сообщение самому себе
                    try:
                        player = await message.bot.get_chat(player_id)
                        await message.bot.send_message(player.id, f'Игрок {new_player_name} присоединился к игре!')
                        await state.set_state(JoinGame.join)
                    except Exception as e:
                        print(f"Ошибка при отправке сообщения игроку {player_id}: {e}")
                else:
                    try:
                        player = await message.bot.get_chat(player_id)
                        await message.bot.send_message(player.id, f'Вы присоединились к игре {game_id}')
                        await state.set_state(JoinGame.join)
                    except Exception as e:
                        print(f"Ошибка при отправке сообщения игроку {player_id}: {e}")
                await message.bot.send_message(player_id, f"Сейчас в лобби {len(lobbies[game_id].players)} игроков."
                                                          f" Для начала игры необходимо еще минимум {6 - len(lobbies[game_id].players)}")
        else:
            await message.answer('Игра с таким ID не найдена. Введите заново')
            await state.set_state(JoinGame.waiting_for_game_id)
    except ValueError:
        await message.answer("Вы ввели не числовое значение. Повторите попытку")

def generate_game_id():
    game_id = random.randint(1000, 9999)
    while game_id in lobbies:
        game_id = random.randint(1000, 9999)
    return game_id
