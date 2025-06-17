from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    Uuid,
)
from sqlalchemy.dialects import postgresql

from ttt.entities.core import GameResult, GameState


metadata = MetaData()


game_state = postgresql.ENUM(GameState, name="game_state")


player_table = Table(
    "players",
    metadata,
    Column("id", Integer(), primary_key=True, nullable=False),
    Column("number_of_wins", Integer(), nullable=False),
    Column("number_of_draws", Integer(), nullable=False),
    Column("number_of_defeats", Integer(), nullable=False),
)


game_table = Table(
    "games",
    metadata,
    Column("id", Uuid(), primary_key=True, nullable=False),
    Column("player1_id", ForeignKey("players.id"), nullable=False),
    Column("player2_id", ForeignKey("players.id"), nullable=False),
    Column("state", game_state, nullable=False),
    Column("number_of_unfilled_cells", Integer(), nullable=False),
)

game_result_table = Table(
    "game_results",
    metadata,
    Column("id", Uuid(), primary_key=True, nullable=False),
    Column("game_id", ForeignKey("games.id"), nullable=False, unique=True),
    Column("winner_id", ForeignKey("players.id"), nullable=True),
)

cell_table = Table(
    "cells",
    metadata,
    Column("id", Uuid(), primary_key=True, nullable=False),
    Column("game_id", ForeignKey("games.id"), nullable=False),
    Column("board_position_x", Integer(), nullable=False),
    Column("board_position_y", Integer(), nullable=False),
    Column("filler_id", ForeignKey("players.id"), nullable=True),
)
