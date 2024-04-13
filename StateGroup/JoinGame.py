from aiogram.fsm.state import State, StatesGroup

class JoinGame(StatesGroup):
    waiting_for_game_id = State()
    join = State()