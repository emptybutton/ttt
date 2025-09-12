from dataclasses import dataclass

from structlog.types import FilteringBoundLogger

from ttt.application.matchmaking_queue.common.matchmaking_queue_log import (
    CommonMatchmakingQueueLog,
)


@dataclass(frozen=True, unsafe_hash=False)
class StructlogCommonMatchmakingQueueLog(CommonMatchmakingQueueLog):
    _logger: FilteringBoundLogger

    async def waiting_for_game_start(
        self,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "waiting_for_game_start",
            user_id=user_id,
        )

    async def double_waiting_for_game_start(
        self,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "double_waiting_for_game_start",
            user_id=user_id,
        )

    async def user_already_in_game_to_add_to_matchmaking_queue(
        self,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_already_in_game_to_add_to_matchmaking_queue",
            user_id=user_id,
        )
