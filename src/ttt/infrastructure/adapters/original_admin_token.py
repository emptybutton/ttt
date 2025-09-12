from collections.abc import Generator
from dataclasses import dataclass
from typing import Any

from ttt.application.user.common.ports.original_admin_token import (
    OriginalAdminToken,
)
from ttt.entities.text.token import Token


@dataclass(frozen=True)
class TokenAsOriginalAdminToken(OriginalAdminToken):
    _token: Token

    def __await__(self) -> Generator[Any, None, Token]:
        return self._get_token().__await__()

    async def _get_token(self) -> Token:
        return self._token
