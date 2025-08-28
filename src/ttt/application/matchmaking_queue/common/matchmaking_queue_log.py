from abc import ABC, abstractmethod


class CommonMatchmakingQueueLog(ABC):
    @abstractmethod
    async def waiting_for_game_start(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def double_waiting_for_game_start(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_already_in_game_to_add_to_matchmaking_queue(
        self, user_id: int, /,
    ) -> None: ...
