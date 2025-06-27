from aiogram.types import Message, Sticker


def parsed_emoji_str(message: Message) -> str | None:
    match message:
        case Message(text=str() as text):
            return text
        case Message(sticker=Sticker(emoji=str() as emoji)):
            return emoji
        case _:
            return None
