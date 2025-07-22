from dataclasses import dataclass, field
from secrets import randbelow
from types import TracebackType

from ttt.application.common.ports.emojis import Emojis
from ttt.entities.text.emoji import Emoji
from ttt.infrastructure.dedublication import Dedublication


@dataclass
class PictographsAsEmojis(Emojis):
    _dedublication: Dedublication[str] = field(
        init=False,
        default_factory=Dedublication,
    )

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._dedublication.forget()

    async def random_emoji(self) -> Emoji:
        """
        :raises ttt.infrastructure.dedublication.GenerationError:
        """

        char = self._dedublication(self._random_char, 768)
        return Emoji(char)

    def _random_char(self) -> str:
        return chr(0x0001F300 + randbelow(768))
