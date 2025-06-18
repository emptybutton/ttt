from dataclasses import dataclass
from uuid import UUID

from ttt.entities.tools.tracking import Tracking


@dataclass
class Player:
    id: int
    number_of_wins: int
    number_of_draws: int
    number_of_defeats: int
    current_game_id: UUID | None

    def be_in_game(self, game_id: UUID) -> None:
        self.current_game_id = game_id

    def lose(self, tracking: Tracking) -> None:
        self.current_game_id = None
        self.number_of_defeats += 1
        tracking.register_mutated(self)

    def win(self, tracking: Tracking) -> None:
        self.current_game_id = None
        self.number_of_wins += 1
        tracking.register_mutated(self)

    def be_draw(self, tracking: Tracking) -> None:
        self.current_game_id = None
        self.number_of_draws += 1
        tracking.register_mutated(self)


def create_player(id_: int, tracking: Tracking) -> Player:
    player = Player(id_, 0, 0, 0, None)
    tracking.register_new(player)

    return player
