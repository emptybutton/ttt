from dataclasses import dataclass
from typing import cast, overload

from aiogram.fsm.context import FSMContext

from ttt.application.user.common.ports.user_fsm import (
    UserFsm,
    UserFsmState,
    WaitingEmojiToBuyState,
    WaitingEmojiToSelectState,
)
from ttt.presentation.aiogram.user.fsm import AiogramUserFsmState


@dataclass(frozen=True, unsafe_hash=False)
class AiogramTrustingUserFsm(UserFsm):
    _context: FSMContext

    @overload
    async def state[T: UserFsmState](
        self,
        type_: type[T],
    ) -> T: ...

    @overload
    async def state[T: UserFsmState](
        self,
        type_: None,
    ) -> None: ...

    async def state[T: UserFsmState](
        self,
        type_: type[T] | None,
    ) -> T | None:
        if type_ is WaitingEmojiToSelectState:
            return cast(T, WaitingEmojiToSelectState())

        if type_ is WaitingEmojiToBuyState:
            return cast(T, WaitingEmojiToBuyState())

        return None

    async def set(self, state: UserFsmState | None) -> None:
        match state:
            case None:
                await self._context.clear()
            case WaitingEmojiToBuyState():
                await self._context.set_state(
                    AiogramUserFsmState.waiting_emoji_to_buy,
                )
            case WaitingEmojiToSelectState():
                await self._context.set_state(
                    AiogramUserFsmState.waiting_emoji_to_select,
                )
