from abc import ABC
from dataclasses import dataclass

from ttt.application.common.ports.fsm import Fsm


@dataclass(frozen=True)
class WaitingEmojiToBuyState: ...


type EmojiPurchaseUserFsmState = WaitingEmojiToBuyState


class EmojiPurchaseUserFsm(Fsm[EmojiPurchaseUserFsmState], ABC): ...
