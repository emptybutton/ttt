from dataclasses import dataclass

from dishka import Provider, Scope, make_async_container
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from httpx import ASGITransport, AsyncClient

from app_name_snake_case.presentation.fastapi.app import (
    FastAPIAppCoroutines,
    FastAPIAppRouters,
    FastAPIAppVersion,
    app_from,
)


@dataclass(kw_only=True, frozen=True, slots=True)
class X:
    x: int


router = APIRouter()


@router.get("/something")
@inject
async def endpoint(x: FromDishka[X]) -> Response:
    return JSONResponse({"x": x.x})


async def test_app_from() -> None:
    provider = Provider(scope=Scope.APP)
    provider.provide(lambda: X(x=4), provides=X)
    provider.provide(
        lambda: FastAPIAppRouters((router, )), provides=FastAPIAppRouters,
    )
    provider.provide(
        lambda: FastAPIAppCoroutines(tuple()), provides=FastAPIAppCoroutines,
    )
    provider.provide(
        lambda: FastAPIAppVersion("0.0.0"), provides=FastAPIAppVersion,
    )
    container = make_async_container(provider)

    app = await app_from(container)

    client = AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost",
    )
    async with client:
        response = await client.get("/something")
        output_json = response.json()

        assert output_json == {"x": 4}
