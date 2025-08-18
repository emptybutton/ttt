
from aiogram.fsm.state import State, StatesGroup


class MainDialogState(StatesGroup):
    main = State()
    emojis = State()
    profile = State()
    game_mode_to_start_game = State()
    ai_type_to_start_game = State()
    game = State()
    completed_game = State()
    shop = State()
    emoji_shop = State()
    stars_shop = State()
