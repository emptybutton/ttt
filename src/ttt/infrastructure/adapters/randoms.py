from random import random

from pydantic.dataclasses import dataclass

from ttt.application.common.ports.randoms import Randoms
from ttt.entities.math.random import Random


@dataclass(frozen=True)
class MersenneTwisterRandoms(Randoms):
    async def random(self) -> Random:
        return Random(random())  # noqa: S311
