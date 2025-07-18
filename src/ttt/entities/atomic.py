from ttt.entities.core.game.game import GameAtomic
from ttt.entities.core.player.player import PlayerAtomic
from ttt.entities.finance.payment.payment import PaymentAtomic


type Atomic = GameAtomic | PlayerAtomic | PaymentAtomic
