from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import SerializableTransaction
from ttt.application.user.common.ports.original_admin_token import (
    OriginalAdminToken,
)
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.user.user import (
    AdminTokenMismatchError,
    UserAlreadyAdminError,
)
from ttt.entities.text.token import Token
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class AuthorizeAsAdmin:
    transaction: SerializableTransaction
    users: Users
    map_: Map
    log: CommonUserLog
    original_admin_token: OriginalAdminToken
    views: CommonUserViews

    async def __call__(self, user_id: int, admin_token: Token) -> None:
        """
        :raises ttt.application.common.errors.serialization_error.SerializationError:
        """  # noqa: E501

        async with self.transaction:
            user, original_admin_token = await gather(
                self.users.user_with_id(user_id),
                self.original_admin_token,
            )

            if user is None:
                await self.transaction.commit()
                await self.views.user_is_not_registered_view(user_id)
                return

            try:
                tracking = Tracking()
                user.authorize_as_admin(
                    admin_token, original_admin_token, tracking,
                )
            except UserAlreadyAdminError:
                await self.log.user_already_admin_to_get_admin_rights(user)
                await self.transaction.commit()
                await self.views.user_already_admin_to_get_admin_rights_view(
                    user,
                )
            except AdminTokenMismatchError:
                await self.log.admin_token_mismatch_to_get_admin_rights(user)
                await self.transaction.commit()
                await self.views.admin_token_mismatch_to_get_admin_rights_view(
                    user,
                )
            else:
                await self.log.user_authorized_as_admin(user)
                await self.map_(tracking)
                await self.transaction.commit()
                await self.views.user_authorized_as_admin_view(user)
