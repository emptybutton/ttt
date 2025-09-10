from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from uuid import UUID

from ttt.entities.core.game.game import Game, start_game
from ttt.entities.core.user.user import User
from ttt.entities.math.matrix import Matrix
from ttt.entities.math.random import Random
from ttt.entities.text.emoji import Emoji
from ttt.entities.tools.assertion import assert_
from ttt.entities.tools.tracking import Tracking


class InvitationToGameState(Enum):
    active = auto()
    auto_cancelled = auto()
    cancelled_by_user = auto()
    rejected = auto()
    accepted = auto()


class InvitationToGameStateIsNotActiveError(Exception): ...


class UserIsNotInvitingUserError(Exception): ...


class UserIsNotInvitedUserError(Exception): ...


@dataclass
class InvitationToGame:
    id_: UUID
    inviting_user: User
    invited_user: User
    invitation_datetime: datetime
    state: InvitationToGameState

    def cancel(self, user_id: int, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.invitation_to_game.UserIsNotInvitingUserError:
        :raises ttt.entities.core.invitation_to_game.InvitationToGameStateIsNotActiveError:
        """  # noqa: E501

        assert_(
            self.inviting_user.id == user_id, else_=UserIsNotInvitingUserError,
        )
        assert_(
            self.state is InvitationToGameState.active,
            else_=InvitationToGameStateIsNotActiveError,
        )

        self.state = InvitationToGameState.cancelled_by_user
        tracking.register_mutated(self)

    def auto_cancel(self, tracking: Tracking) -> None:
        self.state = InvitationToGameState.auto_cancelled
        tracking.register_mutated(self)

    def reject(self, user_id: int, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.invitation_to_game.UserIsNotInvitedUserError:
        :raises ttt.entities.core.invitation_to_game.InvitationToGameStateIsNotActiveError:
        """  # noqa: E501

        assert_(
            self.invited_user.id == user_id, else_=UserIsNotInvitingUserError,
        )
        assert_(
            self.state is InvitationToGameState.active,
            else_=InvitationToGameStateIsNotActiveError,
        )

        self.state = InvitationToGameState.rejected
        tracking.register_mutated(self)

    def accept(  # noqa: PLR0913, PLR0917
        self,
        user_id: int,
        user_random_emoji: Emoji,
        inviting_player_random_emoji: Emoji,
        player_order_random: Random,
        cell_id_matrix: Matrix[UUID],
        game_id: UUID,
        tracking: Tracking,
    ) -> Game:
        """
        :raises ttt.entities.core.invitation_to_game.UserIsNotInvitedUserError:
        :raises ttt.entities.core.invitation_to_game.InvitationToGameStateIsNotActiveError:
        :raises ttt.entities.core.game.game.SameRandomEmojiError:
        :raises ttt.entities.core.game.game.UsersAlreadyInGameError:
        :raises ttt.entities.core.game.board.InvalidCellIDMatrixError:
        """  # noqa: E501

        assert_(
            self.invited_user.id == user_id, else_=UserIsNotInvitingUserError,
        )
        assert_(
            self.state is InvitationToGameState.active,
            else_=InvitationToGameStateIsNotActiveError,
        )

        self.state = InvitationToGameState.accepted
        tracking.register_mutated(self)

        if float(player_order_random) < 0.5:  # noqa: PLR2004
            player1 = self.invited_user
            player1_random_emoji = user_random_emoji

            player2 = self.inviting_user
            player2_random_emoji = inviting_player_random_emoji
        else:
            player2 = self.invited_user
            player2_random_emoji = user_random_emoji

            player1 = self.inviting_user
            player1_random_emoji = inviting_player_random_emoji

        return start_game(
            cell_id_matrix,
            game_id,
            player1,
            player1_random_emoji,
            player2,
            player2_random_emoji,
            tracking,
        )


InvitationToGameAtomic = InvitationToGame


def invite_to_game(
    user: User,
    invited_user: User,
    invitation_to_game_id: UUID,
    current_datetime: datetime,
    tracking: Tracking,
) -> "InvitationToGame":
    invitation_to_game = InvitationToGame(
        id_=invitation_to_game_id,
        inviting_user=user,
        invited_user=invited_user,
        invitation_datetime=current_datetime,
        state=InvitationToGameState.active,
    )
    tracking.register_new(invitation_to_game)
    return invitation_to_game
