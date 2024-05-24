from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_game_keyboard() -> InlineKeyboardMarkup:
    start = InlineKeyboardButton(text="Начать игру", callback_data="/start")
    share = InlineKeyboardButton(text="Поделиться", callback_data="/share")
    keyboard: list[list[InlineKeyboardButton]] = [[start], [share]]
    inline_markup = InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)
    return inline_markup
