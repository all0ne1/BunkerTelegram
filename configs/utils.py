from keyboards import vote_keyboard

from configs.config import lobbies
from keyboards.vote_keyboard import kick_keyboard

async def send_mess(message,game_id):
    sender_name = message.from_user.username or message.from_user.first_name
    for player_id in lobbies[game_id].players:
        if player_id != message.from_user.id:
            try:
                await message.bot.send_message(player_id, f"Игрок {sender_name} написал: {message.text}")
            except Exception as e:
                print(f"Error sending message to {player_id}: {e}")

async def round_message(message,text,game_id):
    for player_id in lobbies[game_id].players:
        try:
            await message.bot.send_message(player_id, text)
        except Exception as e:
            print(f"Error sending message to {player_id}: {e}")



async def show_chosen_card(message, game_id, game_card, sender):
    sender_name = sender
    for player_id in lobbies[game_id].players:
        if player_id != message.from_user.id:
            try:
                await message.bot.send_message(player_id, f"Игрок {sender_name} выбрал карту: {game_card}")
            except Exception as e:
                print(f"Error sending message to {player_id}: {e}")
