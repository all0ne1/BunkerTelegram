from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_start_keyboard() -> InlineKeyboardMarkup:
    play = InlineKeyboardButton(text="Создать игру", callback_data="/create")
    about = InlineKeyboardButton(text="О игре", callback_data="/about")
    author = InlineKeyboardButton(text="Автор", callback_data="/whoami")
    join = InlineKeyboardButton(text="Присоединиться", callback_data="/join")
    keyboard: list[list[InlineKeyboardButton]] = [[play, join], [about, author]]
    inline_markup = InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)
    return inline_markup
