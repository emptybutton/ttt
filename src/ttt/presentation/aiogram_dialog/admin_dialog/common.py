
from aiogram.fsm.state import State, StatesGroup


class AdminDialogState(StatesGroup):
    main = State()
    other_user_profile = State()
