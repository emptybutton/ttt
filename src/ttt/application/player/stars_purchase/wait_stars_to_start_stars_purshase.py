from dataclasses import dataclass

from ttt.application.player.common.ports.player_fsm import PlayerFsm
from ttt.application.player.common.ports.player_views import PlayerViews
from ttt.entities.core.player.location import PlayerLocation


@dataclass(frozen=True, unsafe_hash=False)
class WaitStarsToStartStarsPurshase:
    fsm: PlayerFsm
    player_views: PlayerViews

    async def __call__(self, location: PlayerLocation) -> None:
        await (
            self.player_views
            .render_wait_stars_to_start_stars_purshase_view(location)
        )
