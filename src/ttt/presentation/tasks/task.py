from collections.abc import Callable
from typing import Any, Protocol

from dishka.async_container import AsyncContextWrapper

from ttt.infrastructure.dishka.next_container import NextContainer


class Task(Protocol):
    async def __call__(self, container: NextContainer, /) -> Any: ...  # noqa: ANN401
