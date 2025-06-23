from dataclasses import dataclass, field
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from ttt.application.common.ports.transaction import Transaction
from ttt.entities.tools.assertion import not_none


@dataclass
class InPostgresTransaction(Transaction):
    _session: AsyncSession
    _transaction: AsyncSessionTransaction | None = field(
        init=False, default=None,
    )

    async def __aenter__(self) -> Self:
        self._transaction = await self._session.begin()
        return self

    async def __aexit__(
        self,
        error_type: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        transaction = not_none(self._transaction)
        return await transaction.__aexit__(error_type, error, traceback)
