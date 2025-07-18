from collections.abc import Callable
from dataclasses import dataclass

from ttt.entities.core.stars import Stars
from ttt.entities.tools.assertion import assert_


class NegativeAccountError(Exception): ...


@dataclass(frozen=True)
class Account:
    """
    :raises ttt.entities.user.account.NegativeAccountError:
    """

    stars: Stars

    def __post_init__(self) -> None:
        assert_(self.stars >= 0, else_=NegativeAccountError)

    def map(self, func: Callable[[Stars], Stars]) -> "Account":
        return Account(func(self.stars))
