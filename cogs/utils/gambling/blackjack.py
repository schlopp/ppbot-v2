import typing
from dataclasses import dataclass
from enum import Enum

from .cards import *


class BlackjackState(Enum):
    """
    BlackjackState of a blackjack game.
    """

    DEALER_TURN: int = 1
    DEALER_BUST: int = 2
    DEALER_BLACKJACK: int = 3
    DEALER_WIN: int = 4
    PUSH: int = 5
    PLAYER_TURN: int = 6
    PLAYER_BUST: int = 7
    PLAYER_BLACKJACK: int = 8
    PLAYER_WIN: int = 9
    TIMEOUT: int = 10


class BlackjackAction(Enum):
    """
    Actions that can be taken in a blackjack game.
    """

    HIT: int = 1
    STAND: int = 2
    DOUBLE: int = 3
    SPLIT: int = 4


@dataclass
class BlackjackCardTotal:
    value: int
    soft: bool

    def __init__(self, value: int, soft: bool):
        self.value = value
        self.soft = soft

    def __str__(self):
        if self.soft:
            return f"{self.value}/{self.value - 10}"
        return f"{self.value}"


class BlackjackHand:
    """
    A class to represent a blackjack hand.
    """

    cards: typing.List[Card]

    def __init__(self, deck: Deck):
        self._deck: Deck = deck
        self.cards: typing.List[Card] = [self._deck.draw(), self._deck.draw()]

    def __str__(self):
        cards = [str(i) for i in self.cards]
        return f"`{'` `'.join(cards)}`"

    def hidden(self):
        return f"`{self.cards[0]}` `?`"

    def hit(self) -> Card:
        """
        Draws a card from the deck and adds it to the hand.
        """
        card: Card = self._deck.draw()
        self.cards.append(card)

        return card

    def total_value(self) -> BlackjackCardTotal:
        total = 0
        aces = 0
        for card in self.cards:
            if card.value == Value.ACE:
                aces += 1
            else:
                total += card.value.value if card.value.value < 10 else 10
        soft = False
        if aces > 1:
            total += aces
        elif aces:
            if total + 11 <= 21:
                total += 11
                soft = True
            else:
                total += 1
        return BlackjackCardTotal(total, soft)


class BlackjackGame:
    """
    A blackjack game.
    """

    def __init__(self, deck: Deck):
        self._deck: Deck = deck
        self._deck.shuffle()
        self._player: BlackjackHand = BlackjackHand(self._deck)
        self._dealer: BlackjackHand = BlackjackHand(self._deck)
        total_player: BlackjackCardTotal = self._player.total_value()
        total_dealer: BlackjackCardTotal = self._dealer.total_value()
        if total_player.value == 21:
            if total_dealer.value == 21:
                self.state: BlackjackState = BlackjackState.PUSH
            else:
                self.state: BlackjackState = BlackjackState.PLAYER_BLACKJACK
        elif total_dealer.value == 21:
            self.state: BlackjackState = BlackjackState.DEALER_BLACKJACK
        else:
            self.state: BlackjackState = BlackjackState.PLAYER_TURN

    @property
    def player(self) -> BlackjackHand:
        return self._player

    @property
    def dealer(self) -> BlackjackHand:
        return self._dealer

    @property
    def deck(self) -> Deck:
        return self._deck

    def player_action(self, action: BlackjackAction) -> None:
        """
        Performs an action on the player.
        """

        if self.state != BlackjackState.PLAYER_TURN:
            raise Exception("Player can only take actions in the PLAYER_TURN state.")

        if action == BlackjackAction.HIT:
            self._player.hit()
            total_value: BlackjackCardTotal = self._player.total_value()
            if total_value.value > 21:
                self.state = BlackjackState.PLAYER_BUST
        elif action == BlackjackAction.STAND:
            self.state = BlackjackState.DEALER_TURN

    def dealer_action(self) -> None:
        """
        Performs an action on the dealer.
        """

        if self.state != BlackjackState.DEALER_TURN:
            raise Exception("Dealer can only take actions in the DEALER_TURN state.")

        total_value: BlackjackCardTotal = self._dealer.total_value()
        player_total_value: BlackjackCardTotal = self._player.total_value()
        if total_value.value > 21:
            self.state = BlackjackState.DEALER_BUST
        elif total_value.value >= 17:
            if total_value.value > player_total_value.value:
                self.state = BlackjackState.DEALER_WIN
            elif total_value.value == player_total_value.value:
                self.state = BlackjackState.PUSH
            else:
                self.state = BlackjackState.PLAYER_WIN
        else:
            self._dealer.hit()
            self.state = BlackjackState.DEALER_TURN
        print(total_value)
