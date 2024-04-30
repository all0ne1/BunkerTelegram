from aiogram import types, Router, F

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from keyboards.start_menu import build_start_keyboard
from aiogram.utils.markdown import hbold
from aiogram.fsm.state import default_state

router = Router()



@router.message(Command('start') and default_state)
async def start_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!", reply_markup=build_start_keyboard())

@router.callback_query(F.data == ('/whoami'))
async def whoami_handler(query: CallbackQuery) -> None:
    await query.message.answer("Автор: Андаев Александр. 2 курс РТУ МИРЭА")

@router.message(default_state)
async def echo_handler(message: types.Message, state: FSMContext) -> None:
    try:
        await message.answer("Я вас не понимаю, введите команду из меню")
    except TypeError as e:
        await message.answer("Я сломался(")

