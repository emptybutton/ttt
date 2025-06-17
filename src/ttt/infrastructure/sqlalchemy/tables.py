from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    Table,
)


metadata = MetaData()

user_table = Table(
    "users",
    metadata,
    Column("id", Integer(), primary_key=True, nullable=False),
    Column("number_of_wins", Integer(), nullable=False),
    Column("number_of_draws", Integer(), nullable=False),
    Column("number_of_defeats", Integer(), nullable=False),
)
