from itertools import batched, groupby
from typing import Iterable
from sqlalchemy import join, select
from sqlalchemy.orm import MappedCollection, composite, registry, relationship

from ttt.entities.core import Board, Cell, Game, GameResult, Player
from ttt.entities.math import Matrix, Vector
from ttt.infrastructure.sqlalchemy.tables import (
    cell_table,
    game_result_table,
    game_table,
    metadata,
    player_table,
)


def _mutable[T: type](type_: T) -> T:
    type_.__setattr__ = object.__setattr__  # type: ignore[method-assign, assignment]
    type_.__delattr__ = object.__delattr__  # type: ignore[method-assign, assignment]

    return type_


mapper_registry = registry(metadata=metadata)

mapper_registry.map_imperatively(Player, player_table)

mapper_registry.map_imperatively(
    Cell,
    cell_table,
    properties=dict(
        board_position=composite(
            Vector,
            cell_table.c.board_position_x,
            cell_table.c.board_position_y,
        ),
    ),
)


def create_board(cells: Iterable[Cell]) -> Board:
    groups = list(groupby(cells, key=lambda it: it.board_position[1]))

    groups.sort(key=lambda it: it[0])  # noqa: FURB118
    lines = [
        sorted(line, key=lambda it: it.board_position[0])
        for _, line in groups
    ]

    return Matrix(lines)


mapper_registry.map_imperatively(
    Game,
    game_table,
    properties=dict(
        player1=relationship(
            Player,
            foreign_keys=[game_table.c.player1_id],
            lazy="joined",
            innerjoin=True,
        ),
        player2=relationship(
            Player,
            foreign_keys=[game_table.c.player2_id],
            lazy="joined",
            innerjoin=True,
        ),
        result=relationship(GameResult, lazy="joined"),
        _cells=relationship(Cell, uselist=True),
        board=composite(
            create_board,
            _cells,
        ),
    ),
)

mapper_registry.map_imperatively(_mutable(GameResult), game_result_table)
