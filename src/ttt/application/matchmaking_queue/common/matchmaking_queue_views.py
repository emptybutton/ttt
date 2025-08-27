from abc import ABC, abstractmethod


class CommonMatchmakingQueueViews(ABC):
    @abstractmethod
    async def waiting_for_game_view(self, user_id: int, /) -> None: ...
