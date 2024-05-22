import asyncio
import re


from aiogram import types, Router
from aiogram.fsm.context import FSMContext


from configs.config import lobbies
from configs.config import lobby_to_user_id
from configs.config import id_to_nick
from StateGroup.game_states import game_states


router = Router()

def get_most_voted_player(votes_for_players):
    if len(votes_for_players) == 0:
        return None
    most_voted_player = max(votes_for_players, key=lambda player: len(votes_for_players[player]))
    return most_voted_player


@router.message(game_states.vote_for_kick)
@router.callback_query(lambda query: re.match(r"player_\d+$", query.data))
async def vote_for_kick(query: types.CallbackQuery, state: FSMContext):
    game_id = lobby_to_user_id.get(query.from_user.id)
    current_lobby = lobbies.get(game_id)
    player_id = query.data.split("_")[1]
    selected_player = id_to_nick.get(int(player_id))
    if selected_player:
        if current_lobby.votes_for_players.get(selected_player):
            current_lobby.votes_for_players[selected_player].append(query.from_user.id)
        else:
            current_lobby.votes_for_players[selected_player] = [query.from_user.id]
        await state.set_state(game_states.in_game)
        await query.answer(f"You voted for {selected_player}")
    else:
        await query.answer("Invalid selection!")