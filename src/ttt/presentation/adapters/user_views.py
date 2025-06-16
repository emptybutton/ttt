from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.ports.user_views import UserViews
from ttt.entities.core.user import User
from ttt.infrastructure.sqlalchemy.tables import user_table
from ttt.presentation.fastapi.schemas.output import UserSchema


@dataclass(kw_only=True, frozen=True, slots=True)
class UserSchemasFromPostgres(UserViews[UserSchema, UserSchema | None]):
    session: AsyncSession

    async def view_of_user(self, user: User, /) -> UserSchema:
        return UserSchema(name=user.name)

    async def view_of_user_with_id(
        self, user_id: UUID | None, /,
    ) -> UserSchema | None:
        if user_id is None:
            return None

        user_name: str | None = await self.session.scalar(
            select(user_table.c.name).where(user_table.c.id == user_id),
        )
        if user_name is None:
            return None

        return UserSchema(name=user_name)
