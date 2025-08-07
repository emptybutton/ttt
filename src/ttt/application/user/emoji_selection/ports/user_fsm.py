from abc import ABC
from dataclasses import dataclass

from ttt.application.common.ports.fsm import Fsm


@dataclass(frozen=True)
class WaitingEmojiToSelectState: ...


type EmojiSelectionUserFsmState = WaitingEmojiToSelectState


class EmojiSelectionUserFsm(Fsm[EmojiSelectionUserFsmState], ABC): ...
