from aiogram import types, Router, F


from aiogram.fsm.context import FSMContext
from config import lobbies
from StateGroup.JoinGame import JoinGame

router = Router()


def get_game_id(user_id):
    for game_id, players in lobbies.items():
        if user_id in players['players']:
            return game_id
    return None




@router.message(JoinGame.join)
async def send_message(message: types.Message, state: FSMContext) -> None:
    game_id = get_game_id(message.from_user.id)
    sender_name = message.from_user.username or message.from_user.first_name
    for player_id in lobbies[game_id]['players']:
        if player_id != message.from_user.id:
            try:
                await message.bot.send_message(player_id, f"Игрок {sender_name} написал: {message.text}")
            except Exception as e:
                print(f"Error sending message to {player_id}: {e}")