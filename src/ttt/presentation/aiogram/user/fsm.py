from aiogram.fsm.state import State, StatesGroup


class AiogramUserFsmState(StatesGroup):
    waiting_emoji_to_buy = State()
    waiting_emoji_to_select = State()
