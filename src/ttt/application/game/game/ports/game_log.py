from abc import ABC, abstractmethod

from ttt.entities.core.game.game import Game
from ttt.entities.core.game.move import AiMove, UserMove
from ttt.entities.core.user.user import User


class GameLog(ABC):
    @abstractmethod
    async def game_against_user_started(
        self,
        game: Game,
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
        user_id: int,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_move_maked(
        self,
        user_id: int,
        game: Game,
        move: UserMove,
        /,
    ) -> None: ...

    @abstractmethod
    async def ai_move_maked(
        self,
        user_id: int,
        game: Game,
        move: AiMove,
        /,
    ) -> None: ...

    @abstractmethod
    async def game_completed(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_already_in_game_to_start_game_against_ai(
        self, user: User, /,
    ) -> None:
        ...

    @abstractmethod
    async def already_completed_game_to_make_move(
        self,
        game: Game,
        user_id: int,
        cell_number_int: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def not_current_player_to_make_move(
        self,
        game: Game,
        user_id: int,
        cell_number_int: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_cell_to_make_move(
        self,
        game: Game,
        user_id: int,
        cell_number_int: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def already_filled_cell_to_make_move(
        self,
        game: Game,
        user_id: int,
        cell_number_int: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def already_completed_game_to_cancel(
        self,
        game: Game,
        user_id: int,
        /,
    ) -> None: ...
