from collections.abc import Generator
from dataclasses import dataclass
from uuid import UUID

from ttt.entities.core.game.game import Game, start_game
from ttt.entities.core.user.rank import are_ranks_adjacent
from ttt.entities.core.user.user import User
from ttt.entities.math.matrix import Matrix
from ttt.entities.text.emoji import Emoji
from ttt.entities.tools.combinations import Combinations
from ttt.entities.tools.tracking import Tracking


@dataclass
class MatchmakingInput:
    cell_id_matrix: Matrix[UUID]
    game_id: UUID
    player1_random_emoji: Emoji
    player2_random_emoji: Emoji


@dataclass
class UsersAreNotWaitingForMatchmakingError(Exception):
    users: tuple[User, ...]


def matchmaking(
    users: list[User],
    input_: MatchmakingInput,
    tracking: Tracking,
) -> Generator[Game, MatchmakingInput]:
    """
    :raises ttt.entities.core.user.matchmaking.UsersAreNotWaitingForMatchmakingError
    :raises ttt.entities.core.game.game.SameRandomEmojiError:
    :raises ttt.entities.core.game.board.InvalidCellIDMatrixError:
    """  # noqa: E501

    users_not_waiting_for_matchmaking = tuple(
        user
        for user in users
        if not user.is_waiting_for_matchmaking()
    )
    if users_not_waiting_for_matchmaking:
        raise UsersAreNotWaitingForMatchmakingError(
            users_not_waiting_for_matchmaking,
        )

    for user in list(users):
        if user.is_in_game():
            user.dont_wait_for_matchmaking(tracking)
            users.remove(user)

    combinations = Combinations(users)
    for user1, user2 in combinations:
        if _is_game_allowed(user1, user2):
            user1.dont_wait_for_matchmaking(tracking)
            user2.dont_wait_for_matchmaking(tracking)
            combinations.cut()

            game = start_game(
                input_.cell_id_matrix,
                input_.game_id,
                user1,
                input_.player1_random_emoji,
                user2,
                input_.player2_random_emoji,
                tracking,
            )
            input_ = yield game


def _is_game_allowed(user1: User, user2: User) -> bool:
    rank1 = user1.rank()
    rank2 = user2.rank()

    return rank1 == rank2 or are_ranks_adjacent(rank1, rank2)
