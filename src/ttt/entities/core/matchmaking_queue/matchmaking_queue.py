from dataclasses import dataclass
from datetime import datetime
from itertools import combinations
from uuid import UUID

from ttt.entities.core.game.game import Game, start_game
from ttt.entities.core.matchmaking_queue.user_waiting import UserWaiting
from ttt.entities.core.user.rank import are_ranks_adjacent
from ttt.entities.core.user.user import User, UserAlreadyInGameError
from ttt.entities.math.matrix import Matrix
from ttt.entities.text.emoji import Emoji
from ttt.entities.tools.assertion import assert_
from ttt.entities.tools.tracking import Tracking


class UserAlreadyWaitingForGameError(Exception): ...


@dataclass
class MatchmakingQueue:
    user_waitings: list[UserWaiting]

    def __contains__(self, user: User) -> bool:
        waiting_user_ids = (waiting.user.id for waiting in self.user_waitings)
        return user.id in waiting_user_ids

    def add_user(  # noqa: PLR0913, PLR0917
        self,
        user: User,
        user_waiting_id: UUID,
        cell_id_matrix: Matrix[UUID],
        game_id: UUID,
        player1_random_emoji: Emoji,
        player2_random_emoji: Emoji,
        current_datetime: datetime,
        tracking: Tracking,
    ) -> Game | None:
        """
        :raises ttt.entities.core.matchmaking_queue.matchmaking_queue.UserAlreadyWaitingForGameError:
        :raises ttt.entities.core.game.game.UserAlreadyInGameError:
        :raises ttt.entities.core.game.game.SameRandomEmojiError:
        :raises ttt.entities.core.game.board.InvalidCellIDMatrixError:
        """  # noqa: E501

        assert_(user not in self, else_=UserAlreadyWaitingForGameError)
        assert_(not user.is_in_game(), else_=UserAlreadyInGameError)

        user_waiting = UserWaiting(
            id_=user_waiting_id,
            start_datetime=current_datetime,
            user=user,
        )
        tracking.register_new(user_waiting)
        self.user_waitings.append(user_waiting)

        for user_waiting1, user_waiting2 in combinations(self.user_waitings, 2):
            if self._is_game_allowed(user_waiting1, user_waiting2):
                game = start_game(
                    cell_id_matrix,
                    game_id,
                    user_waiting1.user,
                    player1_random_emoji,
                    user_waiting2.user,
                    player2_random_emoji,
                    tracking,
                )

                self.user_waitings.remove(user_waiting1)
                self.user_waitings.remove(user_waiting2)
                tracking.register_unused(user_waiting1)
                tracking.register_unused(user_waiting2)

                return game

        return None

    def _is_game_allowed(
        self,
        user_waiting1: UserWaiting,
        user_waiting2: UserWaiting,
    ) -> bool:
        rank1 = user_waiting1.user.rank()
        rank2 = user_waiting2.user.rank()

        return rank1 == rank2 or are_ranks_adjacent(rank1, rank2)


MatchmakingQueueAtomic = MatchmakingQueue | UserWaiting
