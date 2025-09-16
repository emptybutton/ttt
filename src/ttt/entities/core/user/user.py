from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from ttt.entities.core.stars import Stars
from ttt.entities.core.user.account import Account
from ttt.entities.core.user.admin_right import (
    AdminRight,
    AdminRightViaAdminToken,
    AdminRightViaOtherAdmin,
)
from ttt.entities.core.user.draw import UserDraw
from ttt.entities.core.user.emoji import UserEmoji
from ttt.entities.core.user.location import UserGameLocation
from ttt.entities.core.user.loss import UserLoss
from ttt.entities.core.user.rank import Rank, rank_for_rating
from ttt.entities.core.user.win import UserWin
from ttt.entities.elo.rating import (
    EloRating,
    GamesPlayed,
    initial_elo_rating,
    new_elo_rating,
)
from ttt.entities.elo.score import WinningScore
from ttt.entities.math.random import Random, deviated_int
from ttt.entities.text.emoji import Emoji
from ttt.entities.text.token import Token
from ttt.entities.tools.assertion import assert_, not_none
from ttt.entities.tools.tracking import Tracking


@dataclass
class UserAlreadyInGameError(Exception):
    user: "User"


@dataclass
class UserNotInGameError(Exception):
    user: "User"


@dataclass
class NotEnoughStarsError(Exception):
    stars_to_become_enough: Stars


class EmojiAlreadyPurchasedError(Exception): ...


class EmojiNotPurchasedError(Exception): ...


class NoPurchaseError(Exception): ...


class UserAlreadyAdminError(Exception): ...


class OtherUserAlreadyAdminError(Exception): ...


class OtherUserIsNotAuthorizedAsAdminViaOtherAdminError(Exception): ...


class AdminTokenMismatchError(Exception): ...


class NotAdminError(Exception): ...


class NotAuthorizedAsAdminViaAdminTokenError(Exception): ...


class UserAlredyAdminToAuthorizeAsAdminError(Exception): ...


@dataclass
class User:
    id: int
    account: Account
    emojis: list[UserEmoji]
    selected_emoji_id: UUID | None
    rating: EloRating
    admin_right: AdminRight | None
    game_location: UserGameLocation | None

    emoji_cost: ClassVar[Stars] = 1000

    def rank(self) -> Rank:
        return rank_for_rating(self.rating)

    def is_admin(self) -> bool:
        return is_user_admin(self.admin_right)

    def authorize_as_admin(
        self,
        user_admin_token: Token,
        original_admin_token: Token,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.user.user.UserAlreadyAdminError:
        :raises ttt.entities.core.user.user.AdminTokenMismatchError:
        """

        assert_(not self.is_admin(), else_=UserAlreadyAdminError)
        assert_(
            user_admin_token == original_admin_token,
            else_=AdminTokenMismatchError,
        )

        self.admin_right = AdminRightViaAdminToken()
        tracking.register_mutated(self)

    def relinquish_admin_right(
        self,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.user.user.NotAdminError:
        """

        assert_(self.is_admin(), else_=NotAdminError)

        self.admin_right = None
        tracking.register_mutated(self)

    def authorize_user_as_admin(
        self,
        user: "User | None",
        user_id: int,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.user.user.NotAuthorizedAsAdminViaAdminTokenError:
        :raises ttt.entities.core.user.user.OtherUserAlreadyAdminError:
        """  # noqa: E501

        assert_(
            isinstance(self.admin_right, AdminRightViaAdminToken),
            else_=NotAuthorizedAsAdminViaAdminTokenError,
        )

        if user is None:
            user = register_user(user_id, tracking)
        else:
            assert_(not user.is_admin(), else_=OtherUserAlreadyAdminError)

        user.admin_right = AdminRightViaOtherAdmin(admin_id=self.id)
        tracking.register_mutated(user)

    def deauthorize_user_as_admin(
        self, user: "User | None", tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.user.user.NotAuthorizedAsAdminViaAdminTokenError:
        :raises ttt.entities.core.user.user.OtherUserIsNotAuthorizedAsAdminViaOtherAdminError:
        """  # noqa: E501

        assert_(
            isinstance(self.admin_right, AdminRightViaAdminToken),
            else_=NotAuthorizedAsAdminViaAdminTokenError,
        )

        user = not_none(
            user, else_=OtherUserIsNotAuthorizedAsAdminViaOtherAdminError,
        )
        assert_(
            isinstance(user.admin_right, AdminRightViaOtherAdmin),
            else_=OtherUserIsNotAuthorizedAsAdminViaOtherAdminError,
        )

        user.admin_right = None
        tracking.register_mutated(user)

    def change_user_account(
        self,
        user: "User | None",
        user_id: int,
        user_account_stars_vector: Stars,
        tracking: Tracking,
    ) -> "User":
        """
        :raises ttt.entities.core.user.user.NotAdminError:
        :raises ttt.entities.user.account.NegativeAccountError:
        """

        assert_(self.is_admin(), else_=NotAdminError)

        if user is None:
            user = register_user(user_id, tracking)

        user.account = user.account.map(
            lambda stars: stars + user_account_stars_vector,
        )
        tracking.register_mutated(user)

        return user

    def set_user_account(
        self,
        user: "User | None",
        user_id: int,
        user_account_stars: Stars,
        tracking: Tracking,
    ) -> "User":
        """
        :raises ttt.entities.core.user.user.NotAdminError:
        :raises ttt.entities.user.account.NegativeAccountError:
        """

        assert_(self.is_admin(), else_=NotAdminError)

        if user is None:
            user = register_user(user_id, tracking)

        user.account = user.account.map(lambda _: user_account_stars)
        tracking.register_mutated(user)

        return user

    def is_in_game(self) -> bool:
        return self.game_location is not None

    def be_in_game(
        self,
        game_id: UUID,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.user.user.UserAlreadyInGameError:
        """

        assert_(not self.is_in_game(), else_=UserAlreadyInGameError(self))

        self.game_location = UserGameLocation(self.id, game_id)
        tracking.register_mutated(self)

    def lose_to_user(
        self,
        enemy_rating: EloRating,
        games_played: GamesPlayed,
        tracking: Tracking,
    ) -> UserLoss:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        """

        self.leave_game(tracking)

        new_rating = new_elo_rating(
            self.rating,
            enemy_rating,
            WinningScore.when_losing,
            games_played,
        )
        rating_vector = new_rating - self.rating
        self.rating = new_rating
        tracking.register_mutated(self)

        return UserLoss(user_id=self.id, rating_vector=rating_vector)

    def lose_to_ai(self, tracking: Tracking) -> UserLoss:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        """

        self.leave_game(tracking)
        tracking.register_mutated(self)

        return UserLoss(user_id=self.id, rating_vector=None)

    def win_against_user(
        self,
        enemy_rating: EloRating,
        games_played: GamesPlayed,
        random: Random,
        tracking: Tracking,
    ) -> UserWin:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        """

        self.leave_game(tracking)
        new_rating = new_elo_rating(
            self.rating,
            enemy_rating,
            WinningScore.when_winning,
            games_played,
        )
        rating_vector = new_rating - self.rating
        self.rating = new_rating

        new_stars = deviated_int(50, 16, random=random)
        self.account = self.account.map(lambda stars: stars + new_stars)

        tracking.register_mutated(self)
        return UserWin(self.id, new_stars, rating_vector)

    def win_against_ai(self, tracking: Tracking) -> UserWin:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        """

        self.leave_game(tracking)
        return UserWin(self.id, new_stars=None, rating_vector=None)

    def be_draw_against_user(
        self,
        enemy_rating: EloRating,
        games_played: GamesPlayed,
        tracking: Tracking,
    ) -> UserDraw:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        """

        self.leave_game(tracking)
        new_rating = new_elo_rating(
            self.rating,
            enemy_rating,
            WinningScore.when_winning,
            games_played,
        )
        rating_vector = new_rating - self.rating
        self.rating = new_rating
        tracking.register_mutated(self)

        return UserDraw(self.id, rating_vector)

    def be_draw_against_ai(self, tracking: Tracking) -> UserDraw:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        """

        self.leave_game(tracking)
        tracking.register_mutated(self)

        return UserDraw(self.id, rating_vector=None)

    def leave_game(self, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        """

        assert_(self.is_in_game(), else_=UserNotInGameError(self))

        self.game_location = None
        tracking.register_mutated(self)

    def buy_emoji(
        self,
        emoji: Emoji,
        purchased_emoji_id: UUID,
        tracking: Tracking,
        current_datetime: datetime,
    ) -> None:
        """
        :raises ttt.entities.core.user.user.EmojiAlreadyPurchasedError:
        :raises ttt.entities.core.user.user.NotEnoughStarsError:
        """

        assert_(
            all(self_emoji.emoji != emoji for self_emoji in self.emojis),
            else_=EmojiAlreadyPurchasedError,
        )

        assert_(
            self.account.stars >= self.emoji_cost,
            NotEnoughStarsError(
                stars_to_become_enough=self.emoji_cost - self.account.stars,
            ),
        )

        self.account = self.account.map(lambda stars: stars - self.emoji_cost)
        tracking.register_mutated(self)

        new_emoji = UserEmoji(
            purchased_emoji_id,
            self.id,
            emoji,
            datetime_of_purchase=current_datetime,
        )
        tracking.register_new(new_emoji)
        self.emojis.append(new_emoji)

        self.selected_emoji_id = new_emoji.id
        tracking.register_mutated(self)

    def emoji(self, random_emoji: Emoji) -> Emoji:
        if self.selected_emoji_id is None:
            return random_emoji

        for self_emoji in self.emojis:
            if self_emoji.id == self.selected_emoji_id:
                return self_emoji.emoji

        raise ValueError

    def select_emoji(self, emoji: Emoji, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.user.user.EmojiNotPurchasedError:
        """

        for self_emoji in self.emojis:
            if self_emoji.emoji == emoji:
                self_emoji_to_select = self_emoji
                break
        else:
            raise EmojiNotPurchasedError

        if self.selected_emoji_id != self_emoji_to_select.id:
            self.selected_emoji_id = self_emoji_to_select.id
        else:
            self.selected_emoji_id = None

        tracking.register_mutated(self)


UserAtomic = User | UserEmoji


def register_user(user_id: int, tracking: Tracking) -> User:
    user = User(
        id=user_id,
        account=Account(0),
        emojis=[],
        selected_emoji_id=None,
        rating=initial_elo_rating,
        game_location=None,
        admin_right=None,
    )
    tracking.register_new(user)

    return user


def is_user_in_game(game_location: UserGameLocation | None) -> bool:
    return game_location is not None


def is_user_admin(admin_right: AdminRight | None) -> bool:
    return admin_right is not None


def user_stars(stars: Stars | None) -> Stars:
    return 0 if stars is None else stars
