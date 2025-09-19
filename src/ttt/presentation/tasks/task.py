from collections.abc import Callable
from typing import Any, Protocol

from dishka.async_container import AsyncContextWrapper


type NextContainer = Callable[[], AsyncContextWrapper]


class Task(Protocol):
    async def __call__(self, container: NextContainer, /) -> Any: ...  # noqa: ANN401
