from dataclasses import dataclass
from typing import cast
from uuid import UUID

from ttt.application.game.common.ports.game_ai_gateway import GameAiGateway
from ttt.entities.core.game.ai import Ai, AiType
from ttt.entities.core.game.game import Game
from ttt.infrastructure.openai.gemini import Gemini
from ttt.infrastructure.openai.promt import next_move_cell_number_promt


@dataclass(frozen=True, unsafe_hash=False)
class GeminiGameAiGateway(GameAiGateway):
    _gemini: Gemini

    async def next_move_cell_number_int(
        self,
        game: Game,
        ai_id: UUID,
        /,
    ) -> int | None:
        if game.player1.id == ai_id:
            ai = cast(Ai, game.player1)
        elif game.player2.id == ai_id:
            ai = cast(Ai, game.player2)
        else:
            raise ValueError

        match ai.type:
            case AiType.gemini_2_0_flash:
                model = "gemini-2.0-flash"

        response = await self._gemini.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": next_move_cell_number_promt(game, ai_id),
                },
            ],
            temperature=1.5,
        )
        content = response.choices[0].message.content

        if content is None:
            return None

        content = content.strip()

        try:
            return int(content)
        except ValueError:
            return None
