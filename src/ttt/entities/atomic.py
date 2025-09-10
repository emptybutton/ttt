from ttt.entities.core.game.game import GameAtomic
from ttt.entities.core.invitation_to_game.invitation_to_game import (
    InvitationToGameAtomic,
)
from ttt.entities.core.matchmaking_queue.matchmaking_queue import (
    MatchmakingQueueAtomic,
)
from ttt.entities.core.user.user import UserAtomic
from ttt.entities.finance.payment.payment import PaymentAtomic


type Atomic = (
    GameAtomic
    | UserAtomic
    | MatchmakingQueueAtomic
    | InvitationToGameAtomic
    | PaymentAtomic
)
