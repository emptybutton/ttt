from dataclasses import dataclass

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.common.ports.map import (
    Map,
    MappableTracking,
    NotUniqueUserIdError,
)
from ttt.infrastructure.sqlalchemy.tables import table_entity


@dataclass(frozen=True, unsafe_hash=True)
class MapToPostgres(Map):
    _session: AsyncSession

    async def __call__(
        self,
        tracking: MappableTracking,
    ) -> None:
        for entity in tracking.new:
            self._session.add(table_entity(entity))

        for entity in tracking.mutated:
            await self._session.merge(table_entity(entity))

        for entity in tracking.unused:
            await self._session.delete(table_entity(entity))

        try:
            await self._session.flush()
        except IntegrityError as error:
            self._handle_integrity_error(error)

    def _handle_integrity_error(self, error: IntegrityError) -> None:
        match error.orig:
            case UniqueViolation() as unique_error:
                constraint_name = unique_error.diag.constraint_name

                if constraint_name == "users_pkey":
                    raise NotUniqueUserIdError from error
            case _: ...

        raise error from error
