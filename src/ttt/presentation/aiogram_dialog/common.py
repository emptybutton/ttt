from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class EncodableToWindowData:
    def window_data(self) -> dict[str, Any]:
        return {self._data_key(): asdict(self)}

    def _data_key(self) -> str:
        return "main"
