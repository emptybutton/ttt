from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from ttt.entities.core.stars import Stars
from ttt.entities.core.user.account import Account
from ttt.entities.core.user.draw import UserDraw
from ttt.entities.core.user.emoji import UserEmoji
from ttt.entities.core.user.last_game import LastGame, last_game
from ttt.entities.core.user.location import UserGameLocation
from ttt.entities.core.user.loss import UserLoss
from ttt.entities.core.user.stars_purchase import StarsPurchase
from ttt.entities.core.user.win import UserWin
from ttt.entities.elo.rating import (
    EloRating,
    initial_elo_rating,
    new_elo_rating,
)
from ttt.entities.elo.score import WinningScore
from ttt.entities.finance.payment.payment import (
    cancel_payment,
    complete_payment,
)
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.entities.math.random import Random, deviated_int
from ttt.entities.text.emoji import Emoji
from ttt.entities.tools.assertion import assert_
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True)
class UserAlreadyInGameError(Exception):
    user: "User"


@dataclass(frozen=True)
class UserNotInGameError(Exception):
    user: "User"


@dataclass(frozen=True)
class NotEnoughStarsError(Exception):
    stars_to_become_enough: Stars


class EmojiAlreadyPurchasedError(Exception): ...


class EmojiNotPurchasedError(Exception): ...


class NoPurchaseError(Exception): ...


class UserAlreadyLeftGameError(Exception): ...


@dataclass
class User:
    id: int
    account: Account
    emojis: list[UserEmoji]
    stars_purchases: list[StarsPurchase]
    last_games: list[LastGame]
    selected_emoji_id: UUID | None
    rating: EloRating

    number_of_wins: int
    number_of_draws: int
    number_of_defeats: int
    game_location: UserGameLocation | None

    emoji_cost: ClassVar[Stars] = 1000

    def games_played(self) -> int:
        return len(self.last_games)

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
        last_game_id: UUID,
        game_id: UUID,
        tracking: Tracking,
    ) -> UserLoss:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        :raises ttt.entities.core.user.user.UserAlreadyLeftGameError:
        """

        self.leave_game(last_game_id, game_id, tracking)

        self.number_of_defeats += 1
        new_rating = new_elo_rating(
            self.rating,
            enemy_rating,
            WinningScore.when_losing,
            self.games_played(),
        )
        rating_vector = new_rating - self.rating
        self.rating = new_rating
        tracking.register_mutated(self)

        return UserLoss(user_id=self.id, rating_vector=rating_vector)

    def lose_to_ai(
        self,
        last_game_id: UUID,
        game_id: UUID,
        tracking: Tracking,
    ) -> UserLoss:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        :raises ttt.entities.core.user.user.UserAlreadyLeftGameError:
        """

        self.leave_game(last_game_id, game_id, tracking)

        self.number_of_defeats += 1
        tracking.register_mutated(self)

        return UserLoss(user_id=self.id, rating_vector=None)

    def win_against_user(
        self,
        enemy_rating: EloRating,
        random: Random,
        last_game_id: UUID,
        game_id: UUID,
        tracking: Tracking,
    ) -> UserWin:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        :raises ttt.entities.core.user.user.UserAlreadyLeftGameError:
        """

        self.leave_game(last_game_id, game_id, tracking)

        self.number_of_wins += 1

        new_rating = new_elo_rating(
            self.rating,
            enemy_rating,
            WinningScore.when_winning,
            self.games_played(),
        )
        rating_vector = new_rating - self.rating
        self.rating = new_rating

        new_stars = deviated_int(50, 16, random=random)
        self.account = self.account.map(lambda stars: stars + new_stars)

        tracking.register_mutated(self)
        return UserWin(self.id, new_stars, rating_vector)

    def win_against_ai(
        self,
        last_game_id: UUID,
        game_id: UUID,
        tracking: Tracking,
    ) -> UserWin:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        :raises ttt.entities.core.user.user.UserAlreadyLeftGameError:
        """

        self.leave_game(last_game_id, game_id, tracking)

        return UserWin(self.id, new_stars=None, rating_vector=None)

    def be_draw_against_user(
        self,
        enemy_rating: EloRating,
        last_game_id: UUID,
        game_id: UUID,
        tracking: Tracking,
    ) -> UserDraw:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        """

        self.leave_game(last_game_id, game_id, tracking)

        self.number_of_draws += 1

        new_rating = new_elo_rating(
            self.rating,
            enemy_rating,
            WinningScore.when_winning,
            self.games_played(),
        )
        rating_vector = new_rating - self.rating
        self.rating = new_rating
        tracking.register_mutated(self)

        return UserDraw(self.id, rating_vector)

    def be_draw_against_ai(
        self,
        last_game_id: UUID,
        game_id: UUID,
        tracking: Tracking,
    ) -> UserDraw:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        """

        self.leave_game(last_game_id, game_id, tracking)

        self.number_of_draws += 1
        tracking.register_mutated(self)

        return UserDraw(self.id, rating_vector=None)

    def leave_game(
        self, last_game_id: UUID, game_id: UUID, tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.user.user.UserNotInGameError:
        :raises ttt.entities.core.user.user.UserAlreadyLeftGameError:
        """

        assert_(self.is_in_game(), else_=UserNotInGameError(self))

        self.game_location = None
        tracking.register_mutated(self)

        assert_(
            (
                self._last_game_with_id(last_game_id) is None
                and self._last_game_with_game_id(game_id) is None
            ),
            else_=UserAlreadyLeftGameError,
        )

        last_game_ = last_game(last_game_id, self.id, game_id, tracking)
        self.last_games.append(last_game_)

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
                self.selected_emoji_id = self_emoji.id
                tracking.register_mutated(self)
                return

        raise EmojiNotPurchasedError

    def remove_selected_emoji(self, tracking: Tracking) -> None:
        self.selected_emoji_id = None
        tracking.register_mutated(self)

    def start_stars_purchase(
        self,
        purchase_id: UUID,
        purchase_stars: Stars,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.stars.InvalidStarsForStarsPurchaseError:
        """

        stars_purchase = StarsPurchase.start(
            purchase_id,
            self.id,
            purchase_stars,
            tracking,
        )
        self.stars_purchases.append(stars_purchase)

    def start_stars_purchase_payment(
        self,
        purchase_id: UUID,
        payment_id: UUID,
        current_datetime: datetime,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.user.user.NoPurchaseError:
        :raises ttt.entities.finance.payment.payment.PaymentIsAlreadyBeingMadeError:
        """  # noqa: E501

        purchase = self._stars_purchase(purchase_id)
        purchase.start_payment(payment_id, current_datetime, tracking)

    def complete_stars_purchase_payment(
        self,
        purchase_id: UUID,
        payment_success: PaymentSuccess,
        current_datetime: datetime,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.user.user.NoPurchaseError:
        :raises ttt.entities.finance.payment.payment.NoPaymentError:
        :raises ttt.entities.finance.payment.payment.PaymentIsNotInProcessError:
        """

        purchase = self._stars_purchase(purchase_id)

        self.account = self.account.map(lambda stars: stars + purchase.stars)
        tracking.register_mutated(self)
        complete_payment(
            purchase.payment,
            payment_success,
            current_datetime,
            tracking,
        )

    def cancel_stars_purchase(
        self,
        purchase_id: UUID,
        current_datetime: datetime,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.user.user.NoPurchaseError:
        :raises ttt.entities.finance.payment.payment.NoPaymentError:
        :raises ttt.entities.finance.payment.payment.PaymentIsNotInProcessError:
        """

        purchase = self._stars_purchase(purchase_id)
        cancel_payment(purchase.payment, current_datetime, tracking)

    def _stars_purchase(self, purchase_id: UUID) -> StarsPurchase:
        """
        :raises ttt.entities.user.user.NoPurchaseError:
        """

        for purchase in self.stars_purchases:
            if purchase.id_ == purchase_id:
                return purchase

        raise NoPurchaseError

    def _last_game_with_id(self, last_game_id: UUID) -> LastGame | None:
        for last_game_ in self.last_games:
            if last_game_.id == last_game_id:
                return last_game_

        return None

    def _last_game_with_game_id(self, game_id: UUID) -> LastGame | None:
        for last_game_ in self.last_games:
            if last_game_.game_id == game_id:
                return last_game_

        return None


type UserAtomic = User | UserEmoji | StarsPurchase | LastGame


def register_user(user_id: int, tracking: Tracking) -> User:
    user = User(
        id=user_id,
        account=Account(0),
        stars_purchases=[],
        last_games=[],
        emojis=[],
        selected_emoji_id=None,
        rating=initial_elo_rating,
        number_of_wins=0,
        number_of_draws=0,
        number_of_defeats=0,
        game_location=None,
    )
    tracking.register_new(user)

    return user
