from dataclasses import dataclass

from aiogram.fsm.context import FSMContext

from ttt.application.user.emoji_purchase.ports.user_fsm import (
    EmojiPurchaseUserFsm,
    EmojiPurchaseUserFsmState,
    WaitingEmojiToBuyState,
)
from ttt.application.user.emoji_selection.ports.user_fsm import (
    EmojiSelectionUserFsm,
    EmojiSelectionUserFsmState,
    WaitingEmojiToSelectState,
)
from ttt.presentation.aiogram.user.fsm import AiogramUserFsmState


@dataclass(frozen=True, unsafe_hash=False)
class AiogramEmojiPurchaseUserFsm(EmojiPurchaseUserFsm):
    _context: FSMContext

    async def state(self, type_: type[EmojiPurchaseUserFsmState]) -> None:
        return

    async def set(self, state: EmojiPurchaseUserFsmState | None) -> None:
        match state:
            case None:
                await self._context.clear()
            case WaitingEmojiToBuyState():
                await self._context.set_state(
                    AiogramUserFsmState.waiting_emoji_to_buy,
                )


@dataclass(frozen=True, unsafe_hash=False)
class AiogramEmojiSelectionUserFsm(EmojiSelectionUserFsm):
    _context: FSMContext

    async def state(self, type_: type[EmojiSelectionUserFsmState]) -> None:
        return

    async def set(self, state: EmojiSelectionUserFsmState | None) -> None:
        match state:
            case None:
                await self._context.clear()
            case WaitingEmojiToSelectState():
                await self._context.set_state(
                    AiogramUserFsmState.waiting_emoji_to_select,
                )
