from typing import cast

from ttt.entities.atomic import Atomic
from ttt.entities.core.game.game import (
    GameAtomic,
)
from ttt.entities.core.invitation_to_game.invitation_to_game import (
    InvitationToGameAtomic,
)
from ttt.entities.core.stars_purchase.stars_purchase import StarsPurchaseAtomic
from ttt.entities.core.user.user import UserAtomic
from ttt.entities.finance.payment.payment import (
    PaymentAtomic,
)
from ttt.infrastructure.sqlalchemy.tables.game import (
    TableGameAtomic,
    table_game_atomic,
)
from ttt.infrastructure.sqlalchemy.tables.invitation_to_game import (
    TableInvitationToGameAtomic,
    table_invitation_to_game_atomic,
)
from ttt.infrastructure.sqlalchemy.tables.payment import (
    TablePaymentAtomic,
    table_payment_atomic,
)
from ttt.infrastructure.sqlalchemy.tables.stars_purchase import (
    TableStarsPurchaseAtomic,
    table_stars_purchase_atomic,
)
from ttt.infrastructure.sqlalchemy.tables.user import (
    TableUserAtomic,
    table_user_atomic,
)


type TableAtomic = (
    TableUserAtomic
    | TableStarsPurchaseAtomic
    | TableGameAtomic
    | TableInvitationToGameAtomic
    | TablePaymentAtomic
    | None
)


def mapped_table_atomic(entity: Atomic) -> TableAtomic:  # noqa: RET503
    if isinstance(entity, UserAtomic):
        return table_user_atomic(entity)

    if isinstance(entity, GameAtomic):
        return table_game_atomic(entity)

    if isinstance(entity, PaymentAtomic):
        return table_payment_atomic(entity)

    if isinstance(entity, InvitationToGameAtomic):
        return table_invitation_to_game_atomic(entity)

    if isinstance(entity, StarsPurchaseAtomic):
        return table_stars_purchase_atomic(entity)


def linked_table_atomic(entity: Atomic) -> TableAtomic:
    if hasattr(entity, "_table_entity"):
        return cast(TableAtomic, entity._table_entity)  # noqa: SLF001

    return None
