from dataclasses import dataclass

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.common.ports.map import (
    Map,
    MappableTracking,
    NotUniquePlayerIdError,
)
from ttt.infrastructure.loading import Loading
from ttt.infrastructure.sqlalchemy.tables import TableModel


@dataclass(frozen=True, unsafe_hash=True)
class MapToPostgres(Map):
    _session: AsyncSession
    _loading: Loading

    async def __call__(
        self,
        tracking: MappableTracking,
    ) -> None:
        # assert False, self._loading

        for entity in tracking.new:
            model = self._loading.loadable(entity)
            if not isinstance(model, TableModel):
                raise TypeError(model)

            self._session.add(model)

        for entity in tracking.mutated:
            model = self._loading.loadable(entity)
            if not isinstance(model, TableModel):
                raise TypeError(model)

            model.map(entity)  # type: ignore[arg-type]

        for entity in tracking.unused:
            model = self._loading.loadable(entity)
            if not isinstance(model, TableModel):
                raise TypeError(model)

            await self._session.delete(model)

        try:
            await self._session.flush()
        except IntegrityError as error:
            self._handle_integrity_error(error)

    def _handle_integrity_error(self, error: IntegrityError) -> None:
        match error.orig:
            case UniqueViolation() as unique_error:
                constraint_name = unique_error.diag.constraint_name

                if constraint_name == "players_pkey":
                    raise NotUniquePlayerIdError from error
            case _:
                raise error from error
