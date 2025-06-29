from ttt.entities.core.game.game import GameAggregate
from ttt.entities.core.player.player import PlayerAggregate
from ttt.entities.finance.payment.payment import PaymentAggregate


type Aggregate = GameAggregate | PlayerAggregate | PaymentAggregate
