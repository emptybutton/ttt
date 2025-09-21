from dataclasses import dataclass

from ttt.application.common.ports.transaction import ReadonlyTransaction, SerializableTransaction
from ttt.application.user.game.ports.user_views import GameUserViews


@dataclass(frozen=True, unsafe_hash=False)
class ViewMatchmaking:
    transaction: ReadonlyTransaction
    views: GameUserViews

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            await self.views.matchmaking_view(user_id)
