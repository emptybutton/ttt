from dataclasses import dataclass, field
from uuid import UUID, uuid4

from structlog.types import EventDict


@dataclass(frozen=True)
class AddRequestId:
    request_id: UUID = field(default_factory=uuid4)

    def __call__(self, _: object, __: str, event_dict: EventDict) -> EventDict:
        event_dict["request_id"] = self.request_id.hex
        return event_dict
