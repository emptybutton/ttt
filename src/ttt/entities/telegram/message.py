from dataclasses import dataclass


@dataclass
class MessageGlobalID:
    message_id: int
    chat_id: int
