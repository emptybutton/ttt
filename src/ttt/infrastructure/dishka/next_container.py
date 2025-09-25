from collections.abc import Mapping
from typing import Any, Protocol

from dishka.async_container import AsyncContextWrapper


class NextContainer(Protocol):
    def __call__(self, context: Mapping[Any, Any] = {}) -> AsyncContextWrapper:
        ...
