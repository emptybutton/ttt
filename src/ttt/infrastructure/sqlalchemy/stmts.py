from collections.abc import Sequence
from typing import cast

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.entities.core.user.rank import UsersWithMaxRating
from ttt.entities.elo.rating import EloRating
from ttt.entities.tools.assertion import not_none
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


async def max_rating_and_users_with_max_rating_from_postgres(
    session: AsyncSession,
) -> tuple[EloRating, UsersWithMaxRating]:
    max_rating_stmt = select(func.max(TableUser.rating))
    max_rating = not_none(await session.scalar(max_rating_stmt))

    raw_users_with_max_rating_stmt = (
        select(func.count(1))
        .select_from(
            select(1)
            .where(TableUser.rating == max_rating)
            .limit(2)
            .subquery(),
        )
    )
    raw_users_with_max_rating = not_none(
        await session.scalar(raw_users_with_max_rating_stmt),
    )
    users_with_max_rating: UsersWithMaxRating = (
        "1" if raw_users_with_max_rating == 1 else ">1"
    )

    return max_rating, users_with_max_rating
