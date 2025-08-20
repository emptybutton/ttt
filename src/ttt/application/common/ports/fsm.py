from abc import ABC, abstractmethod


class InvalidFsmStateError(Exception): ...


class Fsm[StateT](ABC):
    @abstractmethod
    async def state(self, type_: type[StateT]) -> None:
        """
        :raises ttt.application.common.ports.InvalidFsmStateError:
        """

    @abstractmethod
    async def set(self, state: StateT | None) -> None: ...
