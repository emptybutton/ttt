from collections.abc import Callable
from dataclasses import dataclass, field


class GenerationError(Exception): ...


@dataclass(frozen=True)
class Dedublication[V]:
    _generated_values: set[V] = field(default_factory=set, init=False)

    def forget(self) -> None:
        self._generated_values.clear()

    def __call__(self, generator: Callable[[], V], attems: int) -> V:
        """
        :raises ttt.infrastructure.dedublication.GenerationError:
        """

        while attems > 0:
            value = generator()
            attems -= 1

            if value not in self._generated_values:
                self._generated_values.add(value)
                return value

        raise GenerationError
