from pytest import mark

from ttt.entities.core.player.account import Account
from ttt.entities.core.player.player import Player, register_player
from ttt.entities.tools.tracking import Tracking


@mark.parametrize("object_", ["player", "tracking"])
def test_create_player(tracking: Tracking, object_: str) -> None:
    player = register_player(42, tracking)

    if object_ == "player":
        assert player == Player(42, Account(0), 0, 0, 0, None)

    if object_ == "tracking":
        assert len(tracking) == 1
