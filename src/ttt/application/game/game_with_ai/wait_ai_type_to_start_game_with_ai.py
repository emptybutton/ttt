from dataclasses import dataclass

from ttt.application.game.common.ports.game_views import GameViews
from ttt.entities.core.user.location import UserLocation


@dataclass(frozen=True, unsafe_hash=False)
class WaitAiTypeToStartGameWithAi:
    game_views: GameViews

    async def __call__(self, location: UserLocation) -> None:
        await (
            self.game_views
            .render_waiting_for_ai_type_to_start_game_with_ai_view(location)
        )
