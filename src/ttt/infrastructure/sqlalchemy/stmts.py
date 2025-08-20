from collections.abc import Sequence
from typing import cast

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.infrastructure.sqlalchemy.tables.user import TableUser, TableUserEmoji


async def user_emojis_from_postgres(
    session: AsyncSession, user_id: int,
) -> Sequence[str]:
    stmt = (
        select(TableUserEmoji.emoji_str)
        .where(TableUserEmoji.user_id == user_id)
        .order_by(TableUserEmoji.datetime_of_purchase)
    )

    result = await session.scalars(stmt)
    return result.all()


async def selected_user_emoji_str_from_postgres(
    session: AsyncSession, user_id: int,
) -> str | None:
    stmt = (
        select(TableUserEmoji.emoji_str)
        .select_from(TableUser)
        .join(
            TableUserEmoji,
            TableUser.selected_emoji_id == TableUserEmoji.id,
        )
        .where(TableUser.id == user_id)
    )

    return cast(str | None, await session.scalar(stmt))


async def user_exists_in_postgres(session: AsyncSession, user_id: int) -> bool:
    stmt = select(exists(1).where(TableUser.id == user_id))
    return bool(await session.scalar(stmt))
