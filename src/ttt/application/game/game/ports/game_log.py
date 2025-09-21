from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.core.game.game import Game
from ttt.entities.core.game.move import AiMove, UserMove
from ttt.entities.core.user.user import User


class GameLog(ABC):
    @abstractmethod
    async def no_current_game_to_make_move(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_current_game_to_cancel_game(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_game_to_make_ai_move(
        self,
        game_id: UUID,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_current_game(
        self,
        user_id: int,
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
        game: Game,
        move: AiMove,
        ai_id: UUID,
        /,
    ) -> None: ...

    @abstractmethod
    async def game_was_completed_by_user(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def game_was_completed_by_ai(
        self,
        ai_id: UUID,
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

    @abstractmethod
    async def already_completed_game_to_make_ai_move(
        self,
        game: Game,
        ai_id: UUID,
        /,
    ) -> None: ...

    @abstractmethod
    async def not_ai_current_move_to_make_ai_move(
        self,
        game: Game,
        ai_id: UUID,
        /,
    ) -> None: ...
