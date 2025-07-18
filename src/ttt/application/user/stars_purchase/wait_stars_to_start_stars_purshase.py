from dataclasses import dataclass

from ttt.application.user.common.ports.user_fsm import UserFsm
from ttt.application.user.common.ports.user_views import UserViews
from ttt.entities.core.user.location import UserLocation


@dataclass(frozen=True, unsafe_hash=False)
class WaitStarsToStartStarsPurshase:
    fsm: UserFsm
    user_views: UserViews

    async def __call__(self, location: UserLocation) -> None:
        await (
            self.user_views
            .render_wait_stars_to_start_stars_purshase_view(location)
        )
