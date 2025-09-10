from dataclasses import dataclass

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.common.ports.map import (
    Map,
    MappableTracking,
    NotUniqueActiveInvitationToGameUserIdsError,
    NotUniqueUserIdError,
)
from ttt.infrastructure.sqlalchemy.tables.atomic import (
    linked_table_atomic,
    mapped_table_atomic,
)


@dataclass(frozen=True, unsafe_hash=True)
class MapToPostgres(Map):
    _session: AsyncSession

    async def __call__(
        self,
        tracking: MappableTracking,
    ) -> None:
        for table_entity in map(mapped_table_atomic, tracking.new):
            if table_entity is not None:
                self._session.add(table_entity)

        for table_entity in map(mapped_table_atomic, tracking.mutated):
            if table_entity is not None:
                await self._session.merge(table_entity)

        for table_entity in map(linked_table_atomic, tracking.unused):
            if table_entity is not None:
                await self._session.delete(table_entity)

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

                if constraint_name == "ix_invitations_to_game_user_ids":
                    raise NotUniqueActiveInvitationToGameUserIdsError from error
            case _: ...

        raise error from error
