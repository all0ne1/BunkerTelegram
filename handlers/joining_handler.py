import random

from aiogram import types, Router

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from configs.config import lobbies, id_to_nick
from StateGroup.gamestates import GameStates
from configs.config import lobby_by_user_id
from aiogram.utils.markdown import hbold
from keyboards.start_menu import build_start_keyboard
from keyboards.start_game_keyboard import start_game_keyboard


router = Router()


@router.callback_query(lambda query: query.data == "/create")
async def create_callback_handler(query: types.CallbackQuery, state: FSMContext) -> None:
    await query.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    game_id = generate_game_id()
    current_lobby = lobbies[game_id]
    current_lobby.add_player(query.from_user.id)
    current_lobby.game_id = game_id
    current_lobby.make_host(query.from_user.id)
    current_lobby.set_state(GameStates.in_lobby)
    lobby_by_user_id[query.from_user.id] = game_id
    id_to_nick[query.from_user.id] = query.from_user.username or query.from_user.first_name
    await query.message.answer(f"Игра создана! ID игры: {game_id}", reply_markup=start_game_keyboard())
    await state.set_state(GameStates.in_lobby)


async def join_game_logic(message: types.Message, state: FSMContext, game_id: int) -> None:
    if game_id in lobbies and lobbies[game_id].get_state() != GameStates.in_game:
        new_player_name = message.from_user.username or message.from_user.first_name
        lobbies[game_id].add_player(message.from_user.id)
        lobby_by_user_id[message.from_user.id] = game_id

        for player_id in lobbies[game_id].players:
            try:
                player = await message.bot.get_chat(player_id)
                if player_id != message.from_user.id:
                    await message.bot.send_message(player.id, f'Игрок {new_player_name} присоединился к игре!')
                else:
                    await message.bot.send_message(player.id, f'Вы присоединились к игре {game_id}')

                id_to_nick[message.from_user.id] = new_player_name
                await state.set_state(GameStates.in_lobby)
            except Exception as e:
                print(f"Ошибка при отправке сообщения игроку {player_id}: {e}")

            if 4 - len(lobbies[game_id].players) <= 0:
                await message.bot.send_message(player_id, "Минимум игроков достигнут, можно начинать!")
            await message.bot.send_message(player_id, f"Сейчас в лобби {len(lobbies[game_id].players)} игроков."
                                                      f" Для начала игры необходимо еще минимум"
                                                      f" {4 - len(lobbies[game_id].players)}")
    else:
        await message.answer('Игра с таким ID не найдена или игра уже началась. Введите заново')
        await state.set_state(GameStates.waiting_for_game_id)


async def invited_join_handler(message: types.Message, state: FSMContext, game_id) -> None:
    if message.from_user.id in lobbies[game_id].players:
        await message.answer("Вы уже находитесь в этой игре!")
        return
    await join_game_logic(message, state, game_id)


@router.callback_query(lambda query: query.data == "/join")
async def join_callback_handler(query: types.CallbackQuery, state: FSMContext) -> None:
    await query.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    if await state.get_state() != GameStates.in_lobby:
        await query.message.answer("Введите ID игры, к который в хотите присоединиться")
        await state.set_state(GameStates.waiting_for_game_id)
    else:
        await query.message.answer(f"Вы уже находитель в игре {lobby_by_user_id.get(query.from_user.id)}")
        await state.set_state(GameStates.in_lobby)


@router.message(GameStates.waiting_for_game_id)
async def process_join(message: types.Message, state: FSMContext) -> None:
    if message.text == "/exit":
        await message.answer("Вы вышли в меню")
        await message.answer(f"Привет, {hbold(message.from_user.full_name)}!", reply_markup=build_start_keyboard())
        await state.set_state(None)
        return
    try:
        game_id = int(message.text)
        await join_game_logic(message, state, game_id)
    except ValueError:
        await message.answer("Вы ввели не числовое значение. Повторите попытку")


@router.message(Command('exit'))
async def exit_game(message: types.Message, state: FSMContext):
    if await state.get_state() is not None:
        exit_player_name = message.from_user.username or message.from_user.first_name
        game_id = lobby_by_user_id.get(message.from_user.id)
        for player_id in lobbies[game_id].players:
            if player_id != message.from_user.id:
                try:
                    player = await message.bot.get_chat(player_id)
                    await message.bot.send_message(player.id, f'Игрок {exit_player_name} покинул игру!')
                except Exception as e:
                    print(f"Ошибка при отправке сообщения игроку {player_id}: {e}")
            else:
                await message.bot.send_message(player_id, f"Вы покинули игру {game_id}")
        lobbies[game_id].players.remove(message.from_user.id)
        if len(lobbies[game_id].players) == 0:
            del lobbies[game_id]
        await message.answer(f"Привет, {hbold(message.from_user.full_name)}!", reply_markup=build_start_keyboard())
        await state.set_state(None)
    else:
        await message.answer("Вы уже в меню!")


def generate_game_id():
    game_id = random.randint(1000, 9999)
    while game_id in lobbies:
        game_id = random.randint(1000, 9999)
    return game_id
