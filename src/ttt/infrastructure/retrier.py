from collections.abc import Callable
from dataclasses import dataclass, field


type MaxRetries = int
type Retries = int


@dataclass
class Retrier:
    _max_retries_map: dict[type[BaseException], MaxRetries]

    _retries_map: dict[type[BaseException], Retries] = field(
        init=False, default_factory=dict,
    )

    def retry(self) -> bool:
        return bool(self._retries_map)

    async def __call__[**PmT, RT](
        self,
        action: Callable[PmT, RT],
        *args: PmT.args,
        **kwargs: PmT.kwargs,
    ) -> RT:
        while True:
            try:
                return action(*args, **kwargs)
            except BaseException as error:
                if type(error) not in self._max_retries_map:
                    raise error from error

                for error_type, max_retries in self._max_retries_map.items():
                    if not isinstance(error, error_type):
                        continue

                    if error_type not in self._retries_map:
                        self._retries_map[error_type] = 0

                    self._retries_map[error_type] += 1

                    if self._retries_map[error_type] > max_retries:
                        raise error from error
