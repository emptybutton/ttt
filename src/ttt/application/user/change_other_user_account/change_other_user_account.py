from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.change_other_user_account.ports.user_log import (
    ChangeOtherUserAccountLog,
)
from ttt.application.user.change_other_user_account.ports.user_views import (
    ChangeOtherUserAccountViews,
)
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.stars import Stars
from ttt.entities.core.user.account import NegativeAccountError
from ttt.entities.core.user.user import (
    NotAdminError,
)
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class ChangeOtherUserAccount:
    transaction: Transaction
    users: Users
    map_: Map
    log: ChangeOtherUserAccountLog
    common_views: CommonUserViews
    views: ChangeOtherUserAccountViews

    async def __call__(
        self,
        user_id: int,
        other_user_id: int,
        other_user_account_stars_vector: Stars,
    ) -> None:
        async with self.transaction:
            user, other_user = await self.users.users_with_ids(
                (user_id, other_user_id),
            )

            if user is None:
                await self.common_views.user_is_not_registered_view(user_id)
                return

            try:
                tracking = Tracking()
                other_user = user.change_user_account(
                    other_user,
                    other_user_id,
                    other_user_account_stars_vector,
                    tracking,
                )
            except NotAdminError:
                await self.log.user_is_not_admin_to_change_other_user_account(
                    user,
                    other_user,
                    other_user_id,
                    other_user_account_stars_vector,
                )
                await self.common_views.user_is_not_admin_view(user)
            except NegativeAccountError:
                await self.log.negative_account_on_change_other_user_account(
                    user,
                    other_user,
                    other_user_id,
                    other_user_account_stars_vector,
                )
                await (
                    self.views
                    .negative_account_on_change_other_user_account_view(
                        user,
                        other_user,
                        other_user_id,
                        other_user_account_stars_vector,
                    )
                )
            else:
                await self.log.user_changed_other_user_account(
                    user, other_user, other_user_account_stars_vector,
                )
                await self.map_(tracking)
                await self.views.user_changed_other_user_account_view(
                    user, other_user, other_user_account_stars_vector,
                )
