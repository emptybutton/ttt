from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.math.matrix import Matrix, MatrixSize


class UUIDs(ABC):
    @abstractmethod
    async def random_uuid(self) -> UUID: ...

    @abstractmethod
    async def random_uuid_matrix(self, size: MatrixSize) -> Matrix[UUID]: ...
