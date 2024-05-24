import random
import re


from aiogram import types, Router
from aiogram.fsm.context import FSMContext


from configs.config import lobbies
from configs.config import lobby_by_user_id
from configs.config import id_to_nick
from configs.utils import change_one_player_state, round_message, get_id_by_nickname
from StateGroup.gamestates import GameStates
from handlers.in_game_handler import find_id_by_nick
from keyboards.revote_keyboard import revote_keyboard
from keyboards.vote_keyboard import kick_keyboard

router = Router()


def get_most_voted_player(votes_for_players):
    if len(votes_for_players) == 0:
        return None, 0
    sorted_players = sorted(votes_for_players.items(), key=lambda item: len(item[1]), reverse=True)
    top_votes = len(sorted_players[0][1])
    top_players = [player for player, votes in sorted_players if len(votes) == top_votes]
    return top_players, top_votes


@router.message(GameStates.vote_for_kick)
async def vote_for_kick_message(message: types.Message):
    game_id = lobby_by_user_id.get(message.from_user.id)
    current_lobby = lobbies[game_id]
    await message.bot.send_message(message.from_user.id, "Выберите кого хотите изгнать?",
                                   reply_markup=kick_keyboard(current_lobby))


@router.message(GameStates.vote_for_kick)
@router.callback_query(lambda query: re.match(r"player_\d+$", query.data))
async def vote_for_kick(query: types.CallbackQuery, state: FSMContext):
    player_id = query.data.split("_")[1]
    selected_player = id_to_nick.get(int(player_id))
    if selected_player:
        await handle_vote(query, state, selected_player)
    else:
        await query.answer("Invalid selection!")


async def handle_vote(query: types.CallbackQuery, state: FSMContext, selected_player: str):
    game_id = lobby_by_user_id.get(query.from_user.id)
    current_lobby = lobbies.get(game_id)
    player_id = get_id_by_nickname(selected_player, id_to_nick)

    if player_id == query.from_user.id:
        await query.answer("Вы не можете голосовать против себя!")
        return

    if current_lobby.votes_for_players.get(selected_player):
        if query.from_user.id in current_lobby.votes_for_players[selected_player]:
            await query.answer("Вы уже проголосовали против этого игрока!")
            return
        else:
            current_lobby.votes_for_players[selected_player].append(query.from_user.id)
    else:
        current_lobby.votes_for_players[selected_player] = [query.from_user.id]

    await state.set_state(GameStates.in_game)
    await query.answer(f"Вы проголосовали против {selected_player}")

    if sum(len(voters) for voters in current_lobby.votes_for_players.values()) == len(current_lobby.players):
        most_voted_player, top_votes = get_most_voted_player(current_lobby.votes_for_players)
        if most_voted_player is not None:
            if len(most_voted_player) > 1:
                if current_lobby.revote_done:
                    await round_message(query.message, "Голоса разделились во второй раз!"
                                                       " Исключаем случайного игрока", game_id)
                    kicked_player_nick = random.choice(most_voted_player)
                    await round_message(query.message, f"Игрок {kicked_player_nick} изгнан!", game_id)
                    kicked_player = find_id_by_nick(kicked_player_nick)
                    current_lobby.players.remove(kicked_player)
                    current_lobby.player_stats.pop(kicked_player)
                    current_lobby.reset_votes_for_kick()
                    current_lobby.set_state(GameStates.in_game)
                    await change_one_player_state(kicked_player, state, None)
                    return
                current_lobby.set_state(GameStates.revote)
                current_lobby.revote_done = True
                for player_id in current_lobby.players:
                    if id_to_nick.get(player_id) not in most_voted_player:
                        await query.bot.send_message(player_id,
                                                     "Голоса разделились. Проголосуйте снова между этими игроками:",
                                                     reply_markup=revote_keyboard(most_voted_player))
                        await change_one_player_state(player_id, state, GameStates.revote)
                        current_lobby.reset_votes_for_kick()
                    else:
                        await query.bot.send_message(player_id, "Идет переголосование")
            else:
                vote_stats = "\n".join([f"{id_to_nick[voter]} проголосовал за {player}"
                                        for player, voters in current_lobby.votes_for_players.items()
                                        for voter in voters])
                await round_message(query.message, f"Статистика голосования:\n{vote_stats}", game_id)
                await round_message(query.message, f"Игрок {most_voted_player[0]} изгнан!", game_id)
                kicked_player = find_id_by_nick(most_voted_player[0])
                current_lobby.players.remove(kicked_player)
                current_lobby.player_stats.pop(kicked_player)
                current_lobby.reset_votes_for_kick()
                await change_one_player_state(kicked_player, state, None)
