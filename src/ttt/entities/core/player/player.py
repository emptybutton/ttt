from dataclasses import dataclass
from uuid import UUID

from ttt.entities.core.player.account import Account
from ttt.entities.core.player.location import PlayerGameLocation
from ttt.entities.core.player.win import Win
from ttt.entities.math.random import Random, deviated_int
from ttt.entities.tools.assertion import assert_
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True)
class PlayerAlreadyInGameError(Exception):
    player: "Player"


@dataclass(frozen=True)
class PlayerNotInGameError(Exception):
    player: "Player"


@dataclass
class Player:
    id: int
    account: Account
    number_of_wins: int
    number_of_draws: int
    number_of_defeats: int
    game_location: PlayerGameLocation | None

    def is_in_game(self) -> bool:
        return self.game_location is not None

    def be_in_game(
        self,
        game_id: UUID,
        chat_id: int,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.player.player.PlayerAlreadyInGameError:
        """

        assert_(not self.is_in_game(), else_=PlayerAlreadyInGameError(self))

        self.game_location = PlayerGameLocation(self.id, chat_id, game_id)
        tracking.register_mutated(self)

    def lose(self, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.player.player.PlayerNotInGameError:
        """

        self._leave_game(tracking)

        self.number_of_defeats += 1
        tracking.register_mutated(self)

    def win(self, random: Random, tracking: Tracking) -> Win:
        """
        :raises ttt.entities.core.player.player.PlayerNotInGameError:
        """

        self._leave_game(tracking)

        self.number_of_wins += 1

        new_stars = deviated_int(50, 16, random=random)
        self.account = self.account.map(lambda stars: stars + new_stars)

        tracking.register_mutated(self)
        return Win(self.id, new_stars)

    def be_draw(self, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.player.player.PlayerNotInGameError:
        """

        self._leave_game(tracking)

        self.number_of_draws += 1
        tracking.register_mutated(self)

    def _leave_game(self, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.player.player.PlayerNotInGameError:
        """

        assert_(self.is_in_game(), else_=PlayerNotInGameError(self))

        self.game_location = None
        tracking.register_mutated(self)


type PlayerAggregate = Player


def register_player(
    player_id: int,
    tracking: Tracking,
) -> Player:
    player = Player(player_id, Account(0), 0, 0, 0, None)
    tracking.register_new(player)

    return player
