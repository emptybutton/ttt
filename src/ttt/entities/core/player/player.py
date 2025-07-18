from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from ttt.entities.core.player.account import Account
from ttt.entities.core.player.emoji import PlayerEmoji
from ttt.entities.core.player.location import PlayerGameLocation, PlayerLocation
from ttt.entities.core.player.stars_purchase import StarsPurchase
from ttt.entities.core.player.win import Win
from ttt.entities.core.stars import Stars
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
class PlayerAlreadyInGameError(Exception):
    player: "Player"


@dataclass(frozen=True)
class PlayerNotInGameError(Exception):
    player: "Player"


@dataclass(frozen=True)
class NotEnoughStarsError(Exception):
    stars_to_become_enough: Stars


class EmojiAlreadyPurchasedError(Exception): ...


class EmojiNotPurchasedError(Exception): ...


class NoPurchaseError(Exception): ...


@dataclass
class Player:
    id: int
    account: Account
    emojis: list[PlayerEmoji]
    stars_purchases: list[StarsPurchase]
    selected_emoji_id: UUID | None

    number_of_wins: int
    number_of_draws: int
    number_of_defeats: int
    game_location: PlayerGameLocation | None

    emoji_cost: ClassVar[Stars] = 1000

    def is_in_game(self) -> bool:
        return self.game_location is not None

    def be_in_game(
        self,
        game_id: UUID,
        chat_id: int,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.player.player.PlayerAlreadyInGameError:
        """

        assert_(not self.is_in_game(), else_=PlayerAlreadyInGameError(self))

        self.game_location = PlayerGameLocation(self.id, chat_id, game_id)
        tracking.register_mutated(self)

    def lose(self, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.player.player.PlayerNotInGameError:
        """

        self.leave_game(tracking)

        self.number_of_defeats += 1
        tracking.register_mutated(self)

    def win(self, random: Random, tracking: Tracking) -> Win:
        """
        :raises ttt.entities.core.player.player.PlayerNotInGameError:
        """

        self.leave_game(tracking)

        self.number_of_wins += 1

        new_stars = deviated_int(50, 16, random=random)
        self.account = self.account.map(lambda stars: stars + new_stars)

        tracking.register_mutated(self)
        return Win(self.id, new_stars)

    def be_draw(self, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.player.player.PlayerNotInGameError:
        """

        self.leave_game(tracking)

        self.number_of_draws += 1
        tracking.register_mutated(self)

    def leave_game(self, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.player.player.PlayerNotInGameError:
        """

        assert_(self.is_in_game(), else_=PlayerNotInGameError(self))

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
        :raises ttt.entities.core.player.player.EmojiAlreadyPurchasedError:
        :raises ttt.entities.core.player.player.NotEnoughStarsError:
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

        new_emoji = PlayerEmoji(
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
        :raises ttt.entities.core.player.player.EmojiNotPurchasedError:
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
        purchase_chat_id: int,
        purchase_stars: Stars,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.stars.InvalidStarsForStarsPurchaseError:
        """

        stars_purchase = StarsPurchase.start(
            purchase_id,
            PlayerLocation(self.id, purchase_chat_id),
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
        :raises ttt.entities.player.player.NoPurchaseError:
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
        :raises ttt.entities.player.player.NoPurchaseError:
        :raises ttt.entities.finance.payment.payment.NoPaymentError:
        :raises ttt.entities.finance.payment.payment.PaymentIsNotInProcessError:
        """

        purchase = self._stars_purchase(purchase_id)

        self.account = self.account.map(lambda stars: stars + purchase.stars)
        tracking.register_mutated(self)
        complete_payment(
            purchase.payment, payment_success, current_datetime, tracking,
        )

    def cancel_stars_purchase(
        self,
        purchase_id: UUID,
        current_datetime: datetime,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.player.player.NoPurchaseError:
        :raises ttt.entities.finance.payment.payment.NoPaymentError:
        :raises ttt.entities.finance.payment.payment.PaymentIsNotInProcessError:
        """

        purchase = self._stars_purchase(purchase_id)
        cancel_payment(purchase.payment, current_datetime, tracking)

    def _stars_purchase(self, purchase_id: UUID) -> StarsPurchase:
        """
        :raises ttt.entities.player.player.NoPurchaseError:
        """

        for purchase in self.stars_purchases:
            if purchase.id_ == purchase_id:
                return purchase

        raise NoPurchaseError


type PlayerAtomic = Player | PlayerEmoji | StarsPurchase


def register_player(player_id: int, tracking: Tracking) -> Player:
    player = Player(
        id=player_id,
        account=Account(0),
        stars_purchases=[],
        emojis=[],
        selected_emoji_id=None,
        number_of_wins=0,
        number_of_draws=0,
        number_of_defeats=0,
        game_location=None,
    )
    tracking.register_new(player)

    return player
