from dishka import Provider, Scope, make_async_container, provide

from ttt import __version__
from ttt.main.common.di import CommonProvider
from ttt.presentation.fastapi.app import (
    FastAPIAppCoroutines,
    FastAPIAppRouters,
    FastAPIAppVersion,
)
from ttt.presentation.fastapi.routers import all_routers


class FastAPIProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_routers(self) -> FastAPIAppRouters:
        return FastAPIAppRouters(all_routers)

    @provide(scope=Scope.APP)
    def provide_coroutines(self) -> FastAPIAppCoroutines:
        return FastAPIAppCoroutines(tuple())

    @provide(scope=Scope.APP)
    def provide_version(self) -> FastAPIAppVersion:
        return FastAPIAppVersion(__version__)


container = make_async_container(FastAPIProvider(), CommonProvider())
