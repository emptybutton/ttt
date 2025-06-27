from dataclasses import dataclass
from datetime import UTC, datetime

from ttt.application.common.ports.clock import Clock


@dataclass(frozen=True)
class NotMonotonicUtcClock(Clock):
    async def current_datetime(self) -> datetime:
        return datetime.now(UTC)
