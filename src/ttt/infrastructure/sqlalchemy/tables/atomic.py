from ttt.entities.atomic import Atomic
from ttt.entities.core.game.game import (
    GameAtomic,
)
from ttt.entities.core.user.user import UserAtomic
from ttt.entities.finance.payment.payment import (
    PaymentAtomic,
)
from ttt.infrastructure.sqlalchemy.tables.game import (
    TableGameAtomic,
    table_game_atomic,
)
from ttt.infrastructure.sqlalchemy.tables.payment import (
    TablePaymentAtomic,
    table_payment_atomic,
)
from ttt.infrastructure.sqlalchemy.tables.user import (
    TableUserAtomic,
    table_user_atomic,
)


type TableAtomic = TableUserAtomic | TableGameAtomic | TablePaymentAtomic


def table_atomic(entity: Atomic) -> TableAtomic:  # noqa: RET503
    if isinstance(entity, UserAtomic):
        return table_user_atomic(entity)

    if isinstance(entity, GameAtomic):
        return table_game_atomic(entity)

    if isinstance(entity, PaymentAtomic):
        return table_payment_atomic(entity)
