import json
from typing import Literal
from uuid import UUID

from aiogram import Bot
from aiogram.types import LabeledPrice
from pydantic import BaseModel, Field, TypeAdapter

from ttt.entities.core.stars import price_of_stars
from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.stars_purchase import StarsPurchase


class StarsPurshaseInvoicePayload(BaseModel):
    type_: Literal["s"] = "s"
    purshase_id: UUID = Field(alias="s")
    location_user_id: int = Field(alias="p")
    location_chat_id: int = Field(alias="c")

    @classmethod
    def of(
        cls,
        purshase_id: UUID,
        location: UserLocation,
    ) -> "StarsPurshaseInvoicePayload":
        return StarsPurshaseInvoicePayload(
            s=purshase_id,
            p=location.user_id,
            c=location.chat_id,
        )


type InvocePayload = StarsPurshaseInvoicePayload
invoce_payload_adapter = TypeAdapter[InvocePayload](InvocePayload)


async def stars_invoce(
    bot: Bot,
    location: UserLocation,
    purshase: StarsPurchase,
    payments_token: str,
) -> None:
    price = LabeledPrice(
        label=f"{purshase.stars} звёзд",
        amount=price_of_stars(purshase.stars).total_kopecks(),
    )

    payload_model = StarsPurshaseInvoicePayload.of(purshase.id_, location)
    payload = payload_model.model_dump_json(by_alias=True)

    provider_data = json.dumps({
        "receipt": {
            "items": [
                {
                    "description": f"{purshase.stars} звёзд",
                    "quantity": 1,
                    "amount": {
                        "value": float(price_of_stars(purshase.stars)),
                        "currency": "RUB",
                    },
                    "vat_code": 1,
                },
            ],
        },
    })

    await bot.send_invoice(
        location.chat_id,
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
