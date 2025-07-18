from ttt.entities.core.game.game import GameAtomic
from ttt.entities.core.user.user import UserAtomic
from ttt.entities.finance.payment.payment import PaymentAtomic


type Atomic = GameAtomic | UserAtomic | PaymentAtomic
