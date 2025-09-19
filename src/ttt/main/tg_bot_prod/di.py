from dishka import Provider, Scope, provide
from structlog.types import FilteringBoundLogger

from ttt.infrastructure.structlog.logger import prod_logger


class ProdTgBotRequestLoggerProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_request_logger(self) -> FilteringBoundLogger:
        return prod_logger(with_request_id=True)


class ProdTgBotAppLoggerProvider(Provider):
    component = "app"

    @provide(scope=Scope.APP)
    def provide_app_logger(self) -> FilteringBoundLogger:
        return prod_logger(with_request_id=False)
