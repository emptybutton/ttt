from typing import cast

from ttt.entities.atomic import Atomic
from ttt.entities.core.game.game import (
    GameAtomic,
)
from ttt.entities.core.matchmaking_queue.matchmaking_queue import (
    MatchmakingQueueAtomic,
)
from ttt.entities.core.user.user import UserAtomic
from ttt.entities.finance.payment.payment import (
    PaymentAtomic,
)
from ttt.infrastructure.sqlalchemy.tables.game import (
    TableGameAtomic,
    table_game_atomic,
)
from ttt.infrastructure.sqlalchemy.tables.matchmaking_queue import (
    TableMatchmakingQueueAtomic,
    table_matchmaking_queue_atomic,
)
from ttt.infrastructure.sqlalchemy.tables.payment import (
    TablePaymentAtomic,
    table_payment_atomic,
)
from ttt.infrastructure.sqlalchemy.tables.user import (
    TableUserAtomic,
    table_user_atomic,
)


type TableAtomic = (
    TableUserAtomic
    | TableGameAtomic
    | TableMatchmakingQueueAtomic
    | TablePaymentAtomic
)


def mapped_table_atomic(entity: Atomic) -> TableAtomic:  # noqa: RET503
    if isinstance(entity, UserAtomic):
        return table_user_atomic(entity)

    if isinstance(entity, GameAtomic):
        return table_game_atomic(entity)

    if isinstance(entity, PaymentAtomic):
        return table_payment_atomic(entity)

    if isinstance(entity, MatchmakingQueueAtomic):
        return table_matchmaking_queue_atomic(entity)


def linked_table_atomic(entity: Atomic) -> TableAtomic:
    if hasattr(entity, "_table_entity"):
        return cast(TableAtomic, entity._table_entity)  # noqa: SLF001

    return None
