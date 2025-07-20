from abc import ABC, abstractmethod
from collections.abc import Sequence

from ttt.entities.core.game.cell_number import CellNumber
from ttt.entities.core.game.game import AiMove, Game, UserMove
from ttt.entities.core.user.location import UserGameLocation, UserLocation


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
