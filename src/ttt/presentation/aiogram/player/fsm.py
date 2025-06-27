from aiogram.fsm.state import State, StatesGroup


class AiogramPlayerFsmState(StatesGroup):
    waiting_emoji_to_buy = State()
    waiting_emoji_to_select = State()
