from asyncio import sleep
from dataclasses import dataclass

from ttt.application.invitation_to_game.game.auto_cancel_invitations_to_game import (  # noqa: E501
    AutoCancelInvitationsToGame,
)
from ttt.infrastructure.dishka.next_container import NextContainer
from ttt.infrastructure.retrier import Retrier
from ttt.presentation.tasks.task import Task


@dataclass(frozen=True)
class AutoCancelInvitationsToGameTask(Task):
    _interval_seconds: float

    async def __call__(self, container: NextContainer) -> None:
        while True:
            await sleep(self._interval_seconds)
            async with container() as request:
                retrier = await request.get(Retrier)
                cancel_invitations = await request.get(
                    AutoCancelInvitationsToGame,
                )
                await retrier(cancel_invitations)
