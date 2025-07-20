from asyncio import gather
from collections.abc import Sequence
from dataclasses import dataclass

from structlog.types import FilteringBoundLogger

from ttt.application.game.game.ports.game_log import GameLog
from ttt.entities.core.game.game import AiMove, Game, UserMove
from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import User


@dataclass(frozen=True, unsafe_hash=False)
class StructlogGameLog(GameLog):
    _logger: FilteringBoundLogger

    async def waiting_for_game_start(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await self._logger.ainfo(
            "waiting_for_game_start",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )

    async def double_waiting_for_game_start(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await self._logger.ainfo(
            "waiting_for_game_start",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )

    async def game_against_user_started(
        self,
        game: Game,
        /,
    ) -> None:
        await self._logger.ainfo(
            "game_against_user_started",
            game_id=game.id,
        )

    async def user_intends_to_start_game_against_ai(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_intends_to_start_game_against_ai",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )

    async def game_against_ai_started(
        self,
        game: Game,
        /,
    ) -> None:
        await self._logger.ainfo(
            "game_against_ai_started",
            game_id=game.id,
        )

    async def game_cancelled(
        self,
        location: UserLocation,
        game: Game,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_intends_to_start_game_against_ai",
            chat_id=location.chat_id,
            user_id=location.user_id,
            game_id=game.id,
        )

    async def user_move_maked(
        self,
        location: UserLocation,
        game: Game,
        move: UserMove,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_move_maked",
            chat_id=location.chat_id,
            user_id=location.user_id,
            game_id=game.id,
            filled_cell_number=int(move.filled_cell_number),
        )

    async def ai_move_maked(
        self,
        location: UserLocation,
        game: Game,
        move: AiMove,
        /,
    ) -> None:
        await self._logger.ainfo(
            "ai_move_maked",
            chat_id=location.chat_id,
            user_id=location.user_id,
            game_id=game.id,
            filled_cell_number=int(move.filled_cell_number),
            was_move_random=move.was_random,
        )

    async def game_completed(
        self,
        location: UserLocation,
        game: Game,
        /,
    ) -> None:
        await self._logger.ainfo(
            "game_completed",
            chat_id=location.chat_id,
            user_id=location.user_id,
            game_id=game.id,
        )

    async def user_already_in_game_to_start_game(
        self, user: User, location: UserLocation, /,
    ) -> None:
        await self._logger.ainfo(
            "user_already_in_game_to_start_game",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )

    async def already_completed_game_to_make_move(
        self, game: Game, location: UserLocation, cell_number_int: int, /,
    ) -> None:
        await self._logger.ainfo(
            "already_completed_game_to_make_move",
            chat_id=location.chat_id,
            user_id=location.user_id,
            game_id=game.id,
            cell_number_int=cell_number_int,
        )

    async def not_current_player_to_make_move(
        self, game: Game, location: UserLocation, cell_number_int: int, /,
    ) -> None:
        await self._logger.ainfo(
            "not_current_player_to_make_move",
            chat_id=location.chat_id,
            user_id=location.user_id,
            game_id=game.id,
            cell_number_int=cell_number_int,
        )

    async def no_cell_to_make_move(
        self, game: Game, location: UserLocation, cell_number_int: int, /,
    ) -> None:
        await self._logger.ainfo(
            "no_cell_to_make_move",
            chat_id=location.chat_id,
            user_id=location.user_id,
            game_id=game.id,
            cell_number_int=cell_number_int,
        )

    async def already_filled_cell_to_make_move(
        self, game: Game, location: UserLocation, cell_number_int: int, /,
    ) -> None:
        await self._logger.ainfo(
            "already_filled_cell_to_make_move",
            chat_id=location.chat_id,
            user_id=location.user_id,
            game_id=game.id,
            cell_number_int=cell_number_int,
        )

    async def already_completed_game_to_cancel(
        self, game: Game, location: UserLocation, /,
    ) -> None:
        await self._logger.ainfo(
            "already_completed_game_to_cancel_move",
            chat_id=location.chat_id,
            user_id=location.user_id,
            game_id=game.id,
        )

    async def users_already_in_game_to_start_game_via_matchmaking_queue(
        self, locations_of_users_in_game: Sequence[UserLocation], /,
    ) -> None:
        await gather(*(
            self._logger.awarning(
                "user_already_in_game_to_start_game_via_matchmaking_queue",
                chat_id=location.chat_id,
                user_id=location.user_id,
            )
            for location in locations_of_users_in_game
        ))

    async def bad_attempt_to_start_game_via_matchmaking_queue(
        self, locations_of_users_not_in_game: Sequence[UserLocation], /,
    ) -> None:
        await gather(*(
            self._logger.awarning(
                "bad_attempt_to_start_game_via_matchmaking_queue",
                chat_id=location.chat_id,
                user_id=location.user_id,
            )
            for location in locations_of_users_not_in_game
        ))
