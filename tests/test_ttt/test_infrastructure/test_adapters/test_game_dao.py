from uuid import UUID, uuid4

from pytest import fixture, mark
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.entities.core.game.ai import Ai, AiType
from ttt.entities.core.game.cell import Cell
from ttt.entities.core.game.game import Game, GameState
from ttt.entities.core.user.account import Account
from ttt.entities.core.user.location import UserGameLocation
from ttt.entities.core.user.user import User
from ttt.entities.elo.rating import GamesPlayed
from ttt.entities.math.matrix import Matrix
from ttt.entities.text.emoji import Emoji
from ttt.infrastructure.adapters.game_dao import PostgresGameDao
from ttt.infrastructure.sqlalchemy.tables.game import TableGame, TableGameState
from ttt.infrastructure.sqlalchemy.tables.user import TableUser


@fixture
def dao(session: AsyncSession) -> PostgresGameDao:
    return PostgresGameDao(session)


@fixture
def player1() -> User:
    return User(
        id=1,
        account=Account(0),
        emojis=[],
        stars_purchases=[],
        selected_emoji_id=None,
        rating=1000.,
        number_of_wins=0,
        number_of_draws=0,
        number_of_defeats=0,
        game_location=UserGameLocation(1, UUID(int=0)),
        admin_right=None,
    )


@fixture
def player2() -> Ai:
    return Ai(
        id=UUID(int=2),
        type=AiType.gemini_2_0_flash,
    )


@fixture
def game(player1: User, player2: Ai) -> Game:
    return Game(
        id=UUID(int=0),
        player1=player1,
        player1_emoji=Emoji("1"),
        player2=player2,
        player2_emoji=Emoji("2"),
        board=Matrix([
            [
                Cell(UUID(int=0), UUID(int=0), (0, 0), None, None),
                Cell(UUID(int=0), UUID(int=0), (1, 0), None, None),
                Cell(UUID(int=0), UUID(int=0), (2, 0), None, None),
            ],
            [
                Cell(UUID(int=0), UUID(int=0), (0, 1), None, None),
                Cell(UUID(int=0), UUID(int=0), (1, 1), None, None),
                Cell(UUID(int=0), UUID(int=0), (2, 1), None, None),
            ],
            [
                Cell(UUID(int=0), UUID(int=0), (0, 2), None, None),
                Cell(UUID(int=0), UUID(int=0), (1, 2), None, None),
                Cell(UUID(int=0), UUID(int=0), (2, 2), None, None),
            ],
        ]),
        number_of_unfilled_cells=9,
        result=None,
        state=GameState.wait_player1,
    )


@mark.parametrize(
    ("games", "result"),
    [
        (0, "<=30"),
        (5, "<=30"),
        (30, "<=30"),
        (31, ">30"),
        (40, ">30"),
    ],
)
async def test_games_played_by_player_id(
    dao: PostgresGameDao,
    session: AsyncSession,
    game: Game,
    games: int,
    result: GamesPlayed,
) -> None:
    async with session.begin():
        await session.execute(
            insert(TableUser).values({
                "id": 1,
                "rating": 1000,
                "number_of_wins": 0,
                "number_of_draws": 0,
                "number_of_defeats": 0,
            }),
        )
        if games:
            await session.execute(
                insert(TableGame).values([
                    {
                        "id": uuid4(),
                        "user1_id": 1,
                        "state": TableGameState.completed.value,
                    }
                    for _ in range(games)
                ]),
            )

    async with session.begin():
        games_played_by_player_id = await dao.games_played_by_player_id(game)
        assert games_played_by_player_id == {1: result}
