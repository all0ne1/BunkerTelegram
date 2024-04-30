from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def choice_card_keyboard(player) -> InlineKeyboardMarkup:
    profession_button = InlineKeyboardButton(text=f"{player.profession}",callback_data=f"{player.profession}")
    gender_button = InlineKeyboardButton(text=f"{player.gender}",callback_data=f"{player.gender}")
    age_button = InlineKeyboardButton(text=f"{player.age}",callback_data=f"{player.age}")
    health_button = InlineKeyboardButton(text=f"{player.health}",callback_data=f"{player.health}")
    item_button = InlineKeyboardButton(text=f"{player.items}",callback_data=f"{player.items}")
    hobby_button = InlineKeyboardButton(text=f"{player.hobby}",callback_data=f"{player.hobby}")
    fact_button = InlineKeyboardButton(text=f"{player.fact}",callback_data=f"{player.fact}")

    keyboard = [
        [profession_button, gender_button, age_button],
        [health_button, item_button, hobby_button],
        [fact_button]
    ]

    inline_markup = InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)
    return inline_markup