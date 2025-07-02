from typing import Literal
from uuid import UUID

from aiogram import Bot
from aiogram.types import LabeledPrice
from pydantic import BaseModel, Field, TypeAdapter

from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.stars_purchase import StarsPurchase
from ttt.entities.core.stars import price_of_stars


class StarsPurshaseInvoicePayload(BaseModel):
    type_: Literal["s"] = "s"
    purshase_id: UUID = Field(alias="s")
    location_player_id: int = Field(alias="p")
    location_chat_id: int = Field(alias="c")

    @classmethod
    def of(
        cls,
        purshase_id: UUID,
        location: PlayerLocation,
    ) -> "StarsPurshaseInvoicePayload":
        return StarsPurshaseInvoicePayload(
            s=purshase_id,
            p=location.player_id,
            c=location.chat_id,
        )


type InvocePayload = StarsPurshaseInvoicePayload
invoce_payload_adapter = TypeAdapter[InvocePayload](InvocePayload)


async def stars_invoce(
    bot: Bot,
    location: PlayerLocation,
    purshase: StarsPurchase,
    payments_token: str,
) -> None:
    price = LabeledPrice(
        label=f"{purshase.stars} звёзд",
        amount=price_of_stars(purshase.stars).total_kopecks(),
    )

    payload_model = StarsPurshaseInvoicePayload.of(purshase.id_, location)
    payload = payload_model.model_dump_json(by_alias=True)

    await bot.send_invoice(
        location.chat_id,
        title="Звёзды",
        description="Покупка звёзд",
        payload=payload,
        currency="RUB",
        prices=[price],
        is_flexible=False,
        provider_token=payments_token,
    )
