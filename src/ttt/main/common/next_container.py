from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from dishka import AsyncContainer
from dishka.async_container import AsyncContextWrapper

from ttt.infrastructure.dishka.next_container import NextContainer


@dataclass
class NextContainerWithFilledContext(NextContainer):
    _root_container: AsyncContainer
    _context_type_hints: tuple[Any, ...]

    def __call__(
        self, context: Mapping[Any, Any] = {},
    ) -> AsyncContextWrapper:
        return self._root_container(self._filled_context(context))

    def _filled_context(self, context: Mapping[Any, Any]) -> dict[Any, Any]:
        return {
            hint | None: context.get(hint)
            for hint in self._context_type_hints
        }
