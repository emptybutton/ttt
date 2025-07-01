from aiogram import Router
from aiogram.types import PreCheckoutQuery


handle_pre_checkout_query_router = Router(name=__name__)


@handle_pre_checkout_query_router.pre_checkout_query()
async def _(pre_checkout_query: PreCheckoutQuery) -> None:
    await pre_checkout_query.answer(ok=True)
