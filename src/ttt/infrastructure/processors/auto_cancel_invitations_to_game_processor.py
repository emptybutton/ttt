from asyncio import sleep
from dataclasses import dataclass

from structlog.types import FilteringBoundLogger

from ttt.application.invitation_to_game.game.auto_cancel_invitations_to_game import (  # noqa: E501
    AutoCancelInvitationsToGame,
)
from ttt.infrastructure.dishka.next_container import NextContainer
from ttt.infrastructure.processors.processor import Processor
from ttt.infrastructure.retrier import Retrier
from ttt.infrastructure.structlog.logger import unexpected_error_logging


@dataclass(frozen=True)
class AutoCancelInvitationsToGameProcessor(Processor):
    _interval_seconds: float
    _logger: FilteringBoundLogger

    async def __call__(self, container: NextContainer) -> None:
        while True:
            await sleep(self._interval_seconds)
            async with unexpected_error_logging(self._logger):  # noqa: SIM117
                async with container() as request:
                    retrier = await request.get(Retrier)
                    cancel_invitations = await request.get(
                        AutoCancelInvitationsToGame,
                    )
                    await retrier(cancel_invitations)
