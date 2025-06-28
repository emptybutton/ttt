from uuid import UUID

from pytest import fixture

from ttt.entities.core.player.account import Account
from ttt.entities.core.player.location import PlayerGameLocation
from ttt.entities.core.player.player import Player
from ttt.entities.math.random import Random
from ttt.entities.text.emoji import Emoji
from ttt.entities.tools.tracking import Tracking


@fixture
def tracking() -> Tracking:
    return Tracking()


@fixture
def random() -> Random:
    return Random(0.5)


@fixture
def player1() -> Player:
    return Player(
        id=1,
        account=Account(0),
        emojis=[],
        stars_purchases=[],
        selected_emoji_id=None,
        number_of_wins=0,
        number_of_draws=0,
        number_of_defeats=0,
        game_location=PlayerGameLocation(1, 64, UUID(int=0)),
    )


@fixture
def player2() -> Player:
    return Player(
        id=2,
        account=Account(0),
        emojis=[],
        stars_purchases=[],
        selected_emoji_id=None,
        number_of_wins=0,
        number_of_draws=0,
        number_of_defeats=0,
        game_location=PlayerGameLocation(2, 64, UUID(int=0)),
    )


@fixture
def emoji1() -> Emoji:
    return Emoji("1")


@fixture
def emoji2() -> Emoji:
    return Emoji("2")


@fixture
def middle_random() -> Random:
    return Random(0.5)
