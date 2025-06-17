from sqlalchemy.orm import registry

from ttt.entities.core import User
from ttt.infrastructure.sqlalchemy.tables import (
    metadata,
    user_table,
)


mapper_registry = registry(metadata=metadata)

mapper_registry.map_imperatively(User, user_table)

# Alias.__composite_values__ = lambda self: (self.text,)  # type: ignore[attr-defined]  # noqa: E501, ERA001
