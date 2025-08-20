from enum import Enum


type ExpectedScore = float


class WinningScore(Enum):
    when_losing = 0.
    when_drawing = 0.5
    when_winning = 1.
