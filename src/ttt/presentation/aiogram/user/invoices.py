import json
from typing import Literal
from uuid import UUID

from aiogram import Bot
from aiogram.types import LabeledPrice
from pydantic import BaseModel, Field, TypeAdapter

from ttt.entities.core.stars import price_of_stars
from ttt.entities.core.user.stars_purchase import StarsPurchase


class StarsPurchaseInvoicePayload(BaseModel):
    type_: Literal["s"] = "s"
    purchase_id: UUID = Field(alias="s")
    user_id: int = Field(alias="p")

    @classmethod
    def of(
        cls,
        purchase_id: UUID,
        user_id: int,
    ) -> "StarsPurchaseInvoicePayload":
        return StarsPurchaseInvoicePayload(
            s=purchase_id,
            p=user_id,
        )


type InvocePayload = StarsPurchaseInvoicePayload
invoce_payload_adapter = TypeAdapter[InvocePayload](InvocePayload)


async def stars_invoce(
    bot: Bot,
    purchase: StarsPurchase,
    payments_token: str,
) -> None:
    price = LabeledPrice(
        label=f"{purchase.stars} звёзд",
        amount=price_of_stars(purchase.stars).total_kopecks(),
    )

    payload_model = StarsPurchaseInvoicePayload.of(
        purchase.id_, purchase.user_id,
    )
    payload = payload_model.model_dump_json(by_alias=True)

    provider_data = json.dumps({
        "receipt": {
            "items": [
                {
                    "description": f"{purchase.stars} звёзд",
                    "quantity": 1,
                    "amount": {
                        "value": float(price_of_stars(purchase.stars)),
                        "currency": "RUB",
                    },
                    "vat_code": 1,
                },
            ],
        },
    })

    await bot.send_invoice(
        purchase.user_id,
        title="Звёзды",
        description="Покупка звёзд",
        payload=payload,
        currency="RUB",
        prices=[price],
        is_flexible=False,
        provider_token=payments_token,
        need_phone_number=True,
        send_phone_number_to_provider=True,
        provider_data=provider_data,
    )
