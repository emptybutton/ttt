from uuid import UUID

from pytest import fixture

from ttt.entities.core.player import Player
from ttt.entities.tools.tracking import Tracking


@fixture
def tracking() -> Tracking:
    return Tracking()


@fixture
def player1() -> Player:
    return Player(1, 0, 0, 0, UUID(int=0))


@fixture
def player2() -> Player:
    return Player(2, 0, 0, 0, UUID(int=0))
