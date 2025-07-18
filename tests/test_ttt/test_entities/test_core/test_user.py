from pytest import mark

from ttt.entities.core.user.account import Account
from ttt.entities.core.user.user import User, register_user
from ttt.entities.tools.tracking import Tracking


@mark.parametrize("object_", ["user", "tracking"])
def test_create_user(tracking: Tracking, object_: str) -> None:
    user = register_user(42, tracking)

    if object_ == "user":
        assert user == User(42, Account(0), [], [], None, 0, 0, 0, None)

    if object_ == "tracking":
        assert len(tracking) == 1
