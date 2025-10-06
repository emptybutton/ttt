from dataclasses import dataclass

from ttt.application.common.ports.retry import Retry
from ttt.infrastructure.retrier import Retrier


@dataclass
class RetrierRetry(Retry):
    _retries: Retrier

    def __bool__(self) -> bool:
        return self._retries.retry()
