from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime
from uuid import UUID


class InvitationToGameDao(ABC):
    @abstractmethod
    async def set_auto_cancelled_where_invitation_datetime_le_and_active(
        self,
        datetime: datetime,
        /,
    ) -> Sequence[UUID]: ...
