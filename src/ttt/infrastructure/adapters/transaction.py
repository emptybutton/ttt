from dataclasses import dataclass
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.common.ports.transaction import (
    NotSerializableTransaction,
    ReadonlyTransaction,
    SerializableTransaction,
)
from ttt.entities.tools.assertion import assert_, not_none
from ttt.infrastructure.sqlalchemy.serialization import (
    reraise_serialization_error,
)


@dataclass
class InPostgresSerializableTransaction(SerializableTransaction):
    _session: AsyncSession

    async def __aenter__(self) -> Self:
        assert_(not self._session.in_transaction())
        await self._session.connection(
            execution_options={"isolation_level": "SERIALIZABLE"},
        )
        return self

    async def __aexit__(
        self,
        error_type: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        transaction = not_none(self._session.get_transaction())
        with reraise_serialization_error():
            await transaction.__aexit__(error_type, error, traceback)

    async def commit(self) -> None:
        transaction = not_none(self._session.get_transaction())
        with reraise_serialization_error():
            await transaction.commit()


@dataclass
class InPostgresNotSerializableTransaction(NotSerializableTransaction):
    _session: AsyncSession

    async def __aenter__(self) -> Self:
        assert_(not self._session.in_transaction())
        await self._session.connection(
            execution_options={"isolation_level": "READ COMMITED"},
        )
        return self

    async def __aexit__(
        self,
        error_type: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        transaction = not_none(self._session.get_transaction())
        await transaction.__aexit__(error_type, error, traceback)

    async def commit(self) -> None:
        transaction = not_none(self._session.get_transaction())
        await transaction.commit()


@dataclass
class InPostgresReadonlyTransaction(ReadonlyTransaction):
    _session: AsyncSession

    async def __aenter__(self) -> Self:
        assert_(not self._session.in_transaction())
        options = {"isolation_level": "SERIALIZABLE", "readonly": True}
        await self._session.connection(execution_options=options)
        return self

    async def __aexit__(
        self,
        error_type: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        transaction = not_none(self._session.get_transaction())
        await transaction.__aexit__(error_type, error, traceback)
