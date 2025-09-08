from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.user.user import (
    NotAuthorizedAsAdminViaAdminTokenError,
    OtherUserAlreadyAdminError,
    OtherUserIsNotAuthorizedAsAdminViaOtherAdminError,
)
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class DeauthorizeOtherUserAsAdmin:
    transaction: Transaction
    users: Users
    map_: Map
    log: CommonUserLog
    views: CommonUserViews

    async def __call__(self, user_id: int, other_user_id: int) -> None:
        async with self.transaction:
            user, other_user = await self.users.users_with_ids(
                (user_id, other_user_id),
            )

            if user is None:
                await self.views.user_is_not_registered_view(user_id)
                return

            try:
                tracking = Tracking()
                user.deauthorize_user_as_admin(other_user, tracking)
            except NotAuthorizedAsAdminViaAdminTokenError:
                await (
                    self.log
                    .not_authorized_as_admin_via_admin_token_to_deauthorize_other_user_as_admin(
                        user, other_user,
                    )
                )
                await (
                    self.views
                    .not_authorized_as_admin_via_admin_token_to_deauthorize_other_user_as_admin_view(
                        user, other_user,
                    )
                )
            except OtherUserIsNotAuthorizedAsAdminViaOtherAdminError:
                await (
                    self.log
                    .other_user_is_not_authorized_as_admin_via_other_admin_to_deauthorize(
                        user, other_user,
                    )
                )
                await (
                    self.views
                    .other_user_is_not_authorized_as_admin_via_other_admin_to_deauthorize_view(
                        user, other_user,
                    )
                )
            else:
                await self.log.user_deauthorized_other_user_as_admin(
                    user, other_user,
                )
                await self.map_(tracking)
                await self.views.user_deauthorized_other_user_as_admin_view(
                    user, other_user,
                )
