from abc import ABC, abstractmethod

from ttt.application.game.view_models.game_message import GameMessage


class GameChannelTimeoutError(Exception): ...


class GameChannel(ABC):
    @abstractmethod
    async def publish_many(
        self, messages: tuple[GameMessage, ...],
    ) -> None: ...

    @abstractmethod
    async def wait(self, player_id: int) -> (
        GameMessage | GameChannelTimeoutError
    ): ...
