from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ttt.entities.core.user.user import User


@dataclass
class UserWaiting:
    id_: UUID
    start_datetime: datetime
    user: User
