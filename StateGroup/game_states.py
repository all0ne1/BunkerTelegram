from aiogram.fsm.state import State, StatesGroup

class game_states(StatesGroup):
    waiting_for_game_id = State()
    in_lobby = State()
    in_game = State()
    in_game_speaker = State()
    choice_card_to_show = State()
    vote_for_kick = State()