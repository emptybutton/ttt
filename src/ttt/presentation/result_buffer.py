from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResultBuffer:
    result: Any = field(default=None)

    def __call__[T](self, type_: type[T]) -> T:
        if not isinstance(self.result, type_):
            raise TypeError

        return self.result
