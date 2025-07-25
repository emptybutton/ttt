from pytest import mark

from ttt.entities.core.user.account import Account
from ttt.entities.core.user.user import User, register_user
from ttt.entities.tools.tracking import Tracking


@mark.parametrize("object_", ["user", "tracking"])
def test_create_user(tracking: Tracking, object_: str) -> None:
    user = register_user(42, tracking)

    if object_ == "user":
        assert user == User(
            id=42,
            account=Account(0),
            emojis=[],
            stars_purchases=[],
            last_games=[],
            selected_emoji_id=None,
            number_of_wins=0,
            number_of_draws=0,
            number_of_defeats=0,
            game_location=None,
        )

    if object_ == "tracking":
        assert len(tracking) == 1
