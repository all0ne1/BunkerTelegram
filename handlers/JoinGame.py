import random
from aiogram import types, Router, F, Bot


from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import lobbies
from StateGroup.JoinGame import JoinGame
from config import TOKEN

router = Router()



@router.callback_query(lambda query: query.data == "/create")
async def create_callback_handler(query: types.CallbackQuery, state: FSMContext) -> None:
    game_id = generate_game_id()
    lobbies[game_id]['players'].append(query.from_user.id)
    await query.message.answer(f"Игра создана! ID игры: {game_id}")
    print(lobbies)
    await state.set_state(JoinGame.join)


@router.callback_query(lambda query: query.data == "/join")
async def join_callback_handler(query: types.CallbackQuery, state: FSMContext) -> None:
    await query.message.answer("Введите ID игры, к который в хотите присоединиться")
    await state.set_state(JoinGame.waiting_for_game_id)

@router.message(JoinGame.waiting_for_game_id)
async def process_join(message: types.Message, state: FSMContext) -> None:
    game_id = int(message.text)
    try:
        if game_id in lobbies:
            new_player_name = message.from_user.username or message.from_user.first_name
            lobbies[game_id]['players'].append(message.from_user.id)
            for player_id in lobbies[game_id]['players']:
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
        else:
            await message.answer('Игра с таким ID не найдена. Введите заново')
            await state.set_state(JoinGame.waiting_for_game_id)
    except ValueError:
        await state.clear()

def generate_game_id():
    game_id = random.randint(1000, 9999)
    while game_id in lobbies:
        game_id = random.randint(1000, 9999)
    return game_id
