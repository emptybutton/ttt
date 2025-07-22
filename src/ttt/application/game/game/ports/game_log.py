from abc import ABC, abstractmethod
from collections.abc import Sequence

from ttt.entities.core.game.game import AiMove, Game, UserMove
from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import User


class GameLog(ABC):
    @abstractmethod
    async def waiting_for_game_start(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def double_waiting_for_game_start(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def game_against_user_started(
        self,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_intends_to_start_game_against_ai(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def game_against_ai_started(
        self,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def game_cancelled(
        self,
        location: UserLocation,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_move_maked(
        self,
        location: UserLocation,
        game: Game,
        move: UserMove,
        /,
    ) -> None: ...

    @abstractmethod
    async def ai_move_maked(
        self,
        location: UserLocation,
        game: Game,
        move: AiMove,
        /,
    ) -> None: ...

    @abstractmethod
    async def game_completed(
        self,
        location: UserLocation,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_already_in_game_to_start_game(
        self,
        user: User,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def already_completed_game_to_make_move(
        self,
        game: Game,
        location: UserLocation,
        cell_number_int: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def not_current_player_to_make_move(
        self,
        game: Game,
        location: UserLocation,
        cell_number_int: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_cell_to_make_move(
        self,
        game: Game,
        location: UserLocation,
        cell_number_int: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def already_filled_cell_to_make_move(
        self,
        game: Game,
        location: UserLocation,
        cell_number_int: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def already_completed_game_to_cancel(
        self,
        game: Game,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def users_already_in_game_to_start_game_via_matchmaking_queue(
        self,
        locations_of_users_in_game: Sequence[UserLocation],
        /,
    ) -> None: ...

    @abstractmethod
    async def bad_attempt_to_start_game_via_matchmaking_queue(
        self,
        locations_of_users_not_in_game: Sequence[UserLocation],
        /,
    ) -> None: ...
