import asyncio
import logging
import sys


from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.markdown import hbold


TOKEN = "7069557305:AAG_Vx1Iwqkr4S9-mxiJ88oRR9ruGXUazVg"

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    # await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!", reply_markup=build_keyboard())


@dp.message()
async def echo_handler(message: types.Message) -> None:
    try:
        await message.answer("Я вас не понимаю, введите команду из списка")
    except TypeError as e:
        await message.answer("Я сломался(")

def build_keyboard() -> ReplyKeyboardMarkup:
    button1 = KeyboardButton(text="test1")
    button2 = KeyboardButton(text="test2")
    keyboard: list[list[KeyboardButton]] = [[button1, button2]]
    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    return reply_markup


async def main() -> None:
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
