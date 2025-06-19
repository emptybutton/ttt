from abc import ABC, abstractmethod

from ttt.application.common.view_models.player_message import PlayerMessage


class PlayerMessageViews(ABC):
    @abstractmethod
    async def render_message_for_one_player(
        self, message: PlayerMessage, /,
    ) -> None: ...
