import re

from aiogram import types, Router, F

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.start_menu import build_start_keyboard
from handlers.joining_handler import invited_join_handler
from aiogram.utils.markdown import hbold
from aiogram.fsm.state import default_state

router = Router()


@router.message(Command('start'))
async def start_handler(message: types.Message, state: FSMContext) -> None:
    if re.match(r"/start join_lobby_\d+", message.text):
        split = message.text.split("_")
        await invited_join_handler(message, state, int(split[2]))
    else:
        await message.answer(f"Привет, {hbold(message.from_user.full_name)}!", reply_markup=build_start_keyboard())


@router.callback_query(F.data == '/whoami')
async def whoami_handler(query: CallbackQuery) -> None:
    await query.message.answer("Автор: Андаев Александр. 2 курс РТУ МИРЭА")


@router.callback_query(F.data == '/about')
async def about_handler(query: CallbackQuery) -> None:
    with open('configs/game_desc.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        await query.message.answer(content)


@router.message(default_state)
async def echo_handler(message: types.Message) -> None:
    try:
        await message.answer("Я вас не понимаю, введите команду из меню")
    except TypeError:
        await message.answer("Я сломался(")
