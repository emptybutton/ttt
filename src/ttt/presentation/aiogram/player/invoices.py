from typing import Literal

from aiogram import Bot
from aiogram.types import LabeledPrice
from pydantic import BaseModel, Field, TypeAdapter

from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.stars import Stars
from ttt.entities.finance.kopecks import Kopecks
from ttt.entities.finance.rubles import Rubles


class StarsPurshaseInvoicePayload(BaseModel):
    type_: Literal["s"] = "s"
    kopecks: Kopecks = Field(alias="k")
    location_player_id: int = Field(alias="p")
    location_chat_id: int = Field(alias="c")

    @classmethod
    def of(
        cls,
        location: PlayerLocation,
        kopecks: Kopecks,
    ) -> "StarsPurshaseInvoicePayload":
        return StarsPurshaseInvoicePayload(
            p=location.player_id,
            c=location.chat_id,
            k=kopecks,
        )


type InvocePayload = StarsPurshaseInvoicePayload
invoce_payload_adapter = TypeAdapter[InvocePayload](InvocePayload)


async def stars_invoce(
    bot: Bot,
    location: PlayerLocation,
    stars: Stars,
    rubles: Rubles,
    payments_token: str,
) -> None:
    price = LabeledPrice(
        label=f"{stars} звёзд",
        amount=rubles.total_kopecks(),
    )

    payload_model = StarsPurshaseInvoicePayload.of(
        location, rubles.total_kopecks(),
    )
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
