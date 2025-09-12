from abc import abstractmethod

from sqlalchemy.orm import DeclarativeBase


class Base[EntityT](DeclarativeBase):
    __abstract__ = True
    _entity: EntityT | None = None

    def entity(self) -> EntityT:
        if self._entity is not None:
            return self._entity

        entity = self.__entity__()

        entity._table_entity = self  # type: ignore[attr-defined]  # noqa: SLF001
        self._entity = entity

        return entity

    @abstractmethod
    def __entity__(self) -> EntityT: ...
