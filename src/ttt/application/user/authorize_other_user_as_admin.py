from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import SerializableTransaction
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.user.user import (
    NotAuthorizedAsAdminViaAdminTokenError,
    OtherUserAlreadyAdminError,
)
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class AuthorizeOtherUserAsAdmin:
    transaction: SerializableTransaction
    users: Users
    map_: Map
    log: CommonUserLog
    views: CommonUserViews

    async def __call__(self, user_id: int, other_user_id: int) -> None:
        """
        :raises ttt.application.common.errors.serialization_error.SerializationError:
        """  # noqa: E501

        async with self.transaction:
            user, other_user = await self.users.users_with_ids(
                (user_id, other_user_id),
            )

            if user is None:
                await self.transaction.commit()
                await self.views.user_is_not_registered_view(user_id)
                return

            try:
                tracking = Tracking()
                user.authorize_user_as_admin(
                    other_user, other_user_id, tracking,
                )
            except NotAuthorizedAsAdminViaAdminTokenError:
                await (
                    self.log
                    .not_authorized_as_admin_via_admin_token_to_authorize_other_user_as_admin(
                        user, other_user,
                    )
                )
                await self.transaction.commit()
                await (
                    self.views
                    .not_authorized_as_admin_via_admin_token_to_authorize_other_user_as_admin_view(
                        user, other_user,
                    )
                )
            except OtherUserAlreadyAdminError:
                await (
                    self.log
                    .other_user_already_admin_to_authorize_other_user_as_admin(
                        user, other_user,
                    )
                )
                await self.transaction.commit()
                await (
                    self.views
                    .other_user_already_admin_to_authorize_other_user_as_admin_view(
                        user, other_user,
                    )
                )
            else:
                await self.log.user_authorized_other_user_as_admin(
                    user, other_user,
                )
                await self.map_(tracking)
                await self.transaction.commit()
                await self.views.user_authorized_other_user_as_admin_view(
                    user, other_user,
                )
