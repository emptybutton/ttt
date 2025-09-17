from abc import ABC, abstractmethod


class CommonMatchmakingViews(ABC):
    @abstractmethod
    async def waiting_for_game_view(self, user_id: int, /) -> None: ...

    @abstractmethod
    async def double_waiting_for_game_view(self, user_id: int, /) -> None: ...
