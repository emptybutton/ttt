from dataclasses import dataclass

from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_views import GameViews


@dataclass(frozen=True, unsafe_hash=False)
class WaitAiTypeToStartGameWithAi:
    game_views: GameViews
    log: GameLog

    async def __call__(self, user_id: int) -> None:
        await self.game_views.waiting_for_ai_type_to_start_game_with_ai_view(
            user_id,
        )
        await self.log.user_intends_to_start_game_against_ai(user_id)
