from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Any


class SerializableTransaction(AbstractAsyncContextManager[Any], ABC):
    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """
        :raises ttt.application.common.errors.serialization_error.SerializationError:
        """  # noqa: E501

        return None

    @abstractmethod
    async def commit(self) -> None:
        """
        :raises ttt.application.common.errors.serialization_error.SerializationError:
        """  # noqa: E501


class NotSerializableTransaction(AbstractAsyncContextManager[Any], ABC):
    @abstractmethod
    async def commit(self) -> None: ...


class ReadonlyTransaction(AbstractAsyncContextManager[Any], ABC): ...
