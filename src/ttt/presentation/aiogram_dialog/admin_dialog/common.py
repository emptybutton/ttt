
from aiogram.fsm.state import State, StatesGroup


class AdminDialogState(StatesGroup):
    main = State()
    other_user_profile = State()
    authorize_other_user_as_admin = State()
