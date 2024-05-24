import re

from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from StateGroup.gamestates import GameStates
from handlers.vote_for_kick_handler import handle_vote

router = Router()


@router.message(GameStates.revote)
async def revote_echo_handler(message: types.Message):
    await message.answer("Пожалуйста, проголосуйте")


@router.message(GameStates.revote)
@router.callback_query(lambda query: re.match(r"revote_player_.+", query.data))
async def revote_for_kick(query: types.CallbackQuery, state: FSMContext):
    selected_player = query.data.split("_")[2]
    await handle_vote(query, state, selected_player)
