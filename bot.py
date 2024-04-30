import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from configs.config import TOKEN
from handlers import joining_handler, main_chat, in_lobby_handler, in_game_handler

storage = MemoryStorage()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def main() -> None:
    dp = Dispatcher(storage=storage)
    dp.include_routers(joining_handler.router, main_chat.router, in_lobby_handler.router, in_game_handler.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
