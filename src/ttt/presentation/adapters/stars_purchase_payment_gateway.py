from dataclasses import dataclass, field
from uuid import UUID

from aiogram import Bot
from aiogram.types import PreCheckoutQuery
from aiogram_dialog import ShowMode, StartMode

from ttt.application.stars_purchase.ports.stars_purchase_payment_gateway import (  # noqa: E501
    StarsPurchasePaymentGateway,
)
from ttt.entities.core.stars_purchase.stars_purchase import StarsPurchase
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.user.invoices import stars_invoce
from ttt.presentation.aiogram_dialog.common.dialog_manager_for_user import (
    DialogManagerForUser,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


@dataclass
class AiogramPaymentGateway(StarsPurchasePaymentGateway):
    _pre_checkout_query: PreCheckoutQuery | None
    _bot: Bot
    _payments_token: str = field(repr=False)
    _dialog_manager_for_user: DialogManagerForUser

    async def send_invoice(
        self,
        purchase: StarsPurchase,
    ) -> None:
        manager = self._dialog_manager_for_user(purchase.user.id)

        await stars_invoce(self._bot, purchase, self._payments_token)
        await manager.start(
            MainDialogState.stars_shop,
            {"hint": "🌟 Покупайте"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def start_payment(self, payment_id: UUID) -> None:
        await not_none(self._pre_checkout_query).answer(ok=True)

    async def stop_payment_due_to_dublicate(self, payment_id: UUID) -> None:
        message = "С одного инвойса можно покупать только один раз"

        await not_none(self._pre_checkout_query).answer(
            ok=False,
            error_message=message,
        )

    async def stop_payment_due_to_error(self, payment_id: UUID) -> None:
        message = "Неожиданная ошибка. Попробуйте позже!"

        await not_none(self._pre_checkout_query).answer(
            ok=False,
            error_message=message,
        )


# INVOICE
# OK?
# | PAY  | Dulicate
