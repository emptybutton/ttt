from uuid import UUID

from pytest import fixture

from ttt.entities.core.user.account import Account
from ttt.entities.core.user.location import UserGameLocation
from ttt.entities.core.user.user import User
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
def user1() -> User:
    return User(
        id=1,
        account=Account(0),
        emojis=[],
        stars_purchases=[],
        last_games=[],
        selected_emoji_id=None,
        number_of_wins=0,
        number_of_draws=0,
        number_of_defeats=0,
        game_location=UserGameLocation(1, UUID(int=0)),
    )


@fixture
def user2() -> User:
    return User(
        id=2,
        account=Account(0),
        emojis=[],
        stars_purchases=[],
        last_games=[],
        selected_emoji_id=None,
        number_of_wins=0,
        number_of_draws=0,
        number_of_defeats=0,
        game_location=UserGameLocation(2, UUID(int=0)),
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
