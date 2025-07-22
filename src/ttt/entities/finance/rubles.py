from dataclasses import dataclass

from ttt.entities.finance.kopecks import Kopecks
from ttt.entities.tools.assertion import assert_


class InvalidRubleKopecksError(Exception): ...


@dataclass(frozen=True)
class Rubles:
    """
    :raises ttt.entities.finance.rubles.InvalidRubleKopecksError:
    """

    amount: int
    kopecks: Kopecks

    def __post_init__(self) -> None:
        assert_(
            0 <= self.kopecks < 100,  # noqa: PLR2004
            else_=InvalidRubleKopecksError,
        )

    def __float__(self) -> float:
        return self.total_kopecks() / 100

    def __bool__(self) -> bool:
        return bool(self.total_kopecks())

    def total_kopecks(self) -> Kopecks:
        return self.amount * 100 + self.kopecks

    @classmethod
    def with_total_kopecks(cls, total_kopecks: Kopecks) -> "Rubles":
        amount = total_kopecks // 100
        kopecks = total_kopecks - amount * 100

        return Rubles(amount, kopecks)
