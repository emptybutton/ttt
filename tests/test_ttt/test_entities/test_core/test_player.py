
from pytest import mark

from ttt.entities.core.player import Player, create_player
from ttt.entities.tools.tracking import Tracking


@mark.parametrize("object_", ["player", "tracking"])
def test_create_player(tracking: Tracking, object_: str) -> None:
    player = create_player(42, tracking)

    if object_ == "player":
        assert player == Player(42, 0, 0, 0, None)

    if object_ == "tracking":
        assert len(tracking) == 1
