from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def revote_keyboard(players):
    keyboard = []
    for player in players:
        button = InlineKeyboardButton(text=f"{player}", callback_data=f"revote_player_{player}")
        keyboard.append([button])
    inline_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return inline_markup
