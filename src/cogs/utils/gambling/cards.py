import random
import typing
from dataclasses import dataclass
from enum import Enum


class Suit(Enum):
    """
    A class to represent a suit of cards.
    """

    CLUBS: int = 1
    DIAMONDS: int = 2
    HEARTS: int = 3
    SPADES: int = 4


class Value(Enum):
    """
    A class to represent a value of cards.
    """

    ACE: int = 1
    TWO: int = 2
    THREE: int = 3
    FOUR: int = 4
    FIVE: int = 5
    SIX: int = 6
    SEVEN: int = 7
    EIGHT: int = 8
    NINE: int = 9
    TEN: int = 10
    JACK: int = 11
    QUEEN: int = 12
    KING: int = 13


@dataclass
class Card:
    """
    Base class for all cards.
    """

    value: Value
    suit: Suit

    def __init__(self, value: Value, suit: Suit):
        self.value = value
        self.suit = suit

    def __str__(self):
        emojis = {
            Suit.CLUBS: "♣",
            Suit.DIAMONDS: "♦",
            Suit.HEARTS: "♥",
            Suit.SPADES: "♠",
        }
        return f"{emojis[self.suit]} {self.value.name.title()}"

    def __repr__(self):
        return f"BaseCard(name={self.value.name}, value={self.value}, suit={self.suit})"


@dataclass
class Deck:
    """
    A class to represent a deck of cards.
    """

    cards: typing.List[Card]

    def __init__(self):
        self.cards = []
        for i in range(1, 14):
            for j in range(1, 5):
                self.cards.append(Card(Value(i), Suit(j)))

    def shuffle(self):
        """
        Shuffle the deck.
        """

        random.shuffle(self.cards)

    def draw(self):
        """
        Draw a card from the deck.
        """

        return self.cards.pop()

    def __repr__(self):
        return f"Deck(cards={self.cards})"


@dataclass
class Hand:
    """
    A class to represent a hand of cards.
    """

    cards: typing.List[Card]

    def __init__(self):
        self.cards = []

    def add(self, card: Card):
        """
        Add a card to the hand.
        """

        self.cards.append(card)
