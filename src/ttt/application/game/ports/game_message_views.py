from abc import ABC, abstractmethod

from ttt.application.game.view_models.game_message import GameMessage


class GameMessageViews(ABC):
    @abstractmethod
    async def render_message_for_one_player(
        self, message: GameMessage, /,
    ) -> None: ...
