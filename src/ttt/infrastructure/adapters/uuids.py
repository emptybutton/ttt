from dataclasses import dataclass
from uuid import UUID, uuid4

from ttt.application.common.ports.uuids import UUIDs
from ttt.entities.math.matrix import Matrix, MatrixSize


@dataclass(frozen=True)
class UUIDv4s(UUIDs):
    async def random_uuid(self) -> UUID:
        return uuid4()

    async def random_uuid_matrix(self, size: MatrixSize) -> Matrix[UUID]:
        return Matrix([
            [uuid4() for _ in range(size[0])]
            for _ in range(size[1])
        ])
