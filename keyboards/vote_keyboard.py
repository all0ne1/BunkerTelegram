from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from configs.lobby import Lobby
from configs.config import id_to_nick


def kick_keyboard(lobby: Lobby) -> InlineKeyboardMarkup:
    keyboard = []
    for player_id in lobby.players:
        nick = id_to_nick.get(player_id)
        button = InlineKeyboardButton(text=nick, callback_data=f"player_{player_id}")
        print(player_id)
        keyboard.append([button])
    inline_markup = InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)
    return inline_markup
