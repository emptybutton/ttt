from dataclasses import dataclass

from structlog.types import FilteringBoundLogger

from ttt.application.game.game.ports.game_log import GameLog
from ttt.entities.core.game.game import Game
from ttt.entities.core.game.move import AiMove, UserMove
from ttt.entities.core.user.user import User


@dataclass(frozen=True, unsafe_hash=False)
class StructlogGameLog(GameLog):
    _logger: FilteringBoundLogger

    async def game_against_user_started(
        self,
        game: Game,
        /,
    ) -> None:
        await self._logger.ainfo(
            "game_against_user_started",
            game_id=game.id.hex,
        )

    async def game_against_ai_started(
        self,
        game: Game,
        /,
    ) -> None:
        await self._logger.ainfo(
            "game_against_ai_started",
            game_id=game.id.hex,
        )

    async def game_cancelled(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        await self._logger.ainfo(
            "game_cancelled",
            user_id=user_id,
            game_id=game.id.hex,
        )

    async def user_move_maked(
        self,
        user_id: int,
        game: Game,
        move: UserMove,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_move_maked",
            user_id=user_id,
            game_id=game.id.hex,
            filled_cell_number=int(move.filled_cell_number),
        )

    async def ai_move_maked(
        self,
        user_id: int,
        game: Game,
        move: AiMove,
        /,
    ) -> None:
        await self._logger.ainfo(
            "ai_move_maked",
            user_id=user_id,
            game_id=game.id.hex,
            filled_cell_number=int(move.filled_cell_number),
            was_move_random=move.was_random,
        )

    async def game_completed(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        await self._logger.ainfo(
            "game_completed",
            user_id=user_id,
            game_id=game.id.hex,
        )

    async def already_completed_game_to_make_move(
        self,
        game: Game,
        user_id: int,
        cell_number_int: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "already_completed_game_to_make_move",
            user_id=user_id,
            game_id=game.id.hex,
            cell_number_int=cell_number_int,
        )

    async def not_current_player_to_make_move(
        self,
        game: Game,
        user_id: int,
        cell_number_int: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "not_current_player_to_make_move",
            user_id=user_id,
            game_id=game.id.hex,
            cell_number_int=cell_number_int,
        )

    async def no_cell_to_make_move(
        self,
        game: Game,
        user_id: int,
        cell_number_int: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "no_cell_to_make_move",
            user_id=user_id,
            game_id=game.id.hex,
            cell_number_int=cell_number_int,
        )

    async def already_filled_cell_to_make_move(
        self,
        game: Game,
        user_id: int,
        cell_number_int: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "already_filled_cell_to_make_move",
            user_id=user_id,
            game_id=game.id.hex,
            cell_number_int=cell_number_int,
        )

    async def already_completed_game_to_cancel(
        self,
        game: Game,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "already_completed_game_to_cancel_move",
            user_id=user_id,
            game_id=game.id.hex,
        )

    async def user_already_in_game_to_start_game_against_ai(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_already_in_game_to_start_game_against_ai",
            user_id=user.id,
        )

    async def current_game_viewed(
        self,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "current_game_viewed",
            user_id=user_id,
        )
