from abc import ABC
from collections.abc import Awaitable

from ttt.entities.text.token import Token


class OriginalAdminToken(ABC, Awaitable[Token]): ...
