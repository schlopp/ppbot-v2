import random
import typing
from dataclasses import dataclass

__all__ = (
    "DonatorQuotes",
    "Donator",
    "Donators",
)


class _DonatorQuotesDict(typing.TypedDict):
    success: typing.List[str]
    fail: typing.List[str]


@dataclass
class DonatorQuotes:
    """
    A dataclass containing all the quotes that can be said by a donator.

    Attributes
    ----------
    success : list of str
        A list of quotes used when a user get's a reward. This will be formatted with the user's reward.
    failure : list of str
        A list of quotes used when a user doesn't get a reward.

    Examples
    --------

    How the `success` attribute is formatted:

    >>> "You got {} for begging!"
    "You got **2x :alien: Alien** for begging!"
    """

    success: typing.List[str]
    fail: typing.List[str]

    @classmethod
    def from_dict(cls, data: _DonatorQuotesDict) -> "DonatorQuotes":
        return cls(**data)


class _DonatorDict(typing.TypedDict):
    name: str
    quotes: _DonatorQuotesDict
    icon_url: typing.Optional[str]


@dataclass
class Donator:
    """
    A dataclass representing a "Donator". This is a person/character with it's own name, icon (optional) and quotes.
    Represents a "donator". This is a person/character with it's own name, icon_url, and quotes.

    Attributes
    ----------
    name : str
        The name of the donator.
    quotes : DonatorQuotes
        The quotes that can be said by the donator.
    icon_url : str, optional
        The URL of the donator's icon. Should be a picture representing them. Square size recommended.
    """

    name: str
    quotes: DonatorQuotes
    icon_url: typing.Optional[str] = None

    @classmethod
    def from_dict(cls, data: _DonatorDict) -> "Donator":
        return cls(
            name=data["name"],
            quotes=DonatorQuotes.from_dict(data["quotes"]),
            icon_url=data["icon_url"],
        )


class _DonatorsDict(typing.TypedDict):
    donators: typing.List[_DonatorDict]


@dataclass
class Donators:
    """
    A dataclass containing a list of `Donator`s, and some helper functions.

    Attributes
    ----------
    donators : list of Donator
        The list of Donators.
    """

    donators: typing.List[Donator]

    def __init__(self, *donators: Donator):
        self.donators = list(donators)

    @classmethod
    def from_dict(cls, data: _DonatorsDict) -> "Donators":
        return cls(*[Donator.from_dict(x) for x in data["donators"]])

    def get_donator(self, name: str) -> typing.Optional[Donator]:
        """
        Gets a `Donator` from the list of `Donator`s.

        Parameters
        ----------
        name : str
            The name of the `Donator` you're trying to retrieve.

        Returns
        -------
        Donator
            The `Donator` with the given name.
        None
            If no `Donator` object with the given name exists within `self.donators`.
        """

        return next((x for x in self.donators if x.name == name))

    def get_random_donator(self) -> typing.Optional[Donator]:
        """
        Gets a random `Donator` from the list of `Donator`s.

        Parameters
        ----------
        name : str
            The name of the `Donator` you're trying to retrieve.

        Returns
        -------
        Donator
            The random `Donator` object chosen.
        None
            If `self.donators` is empty.
        """

        return random.choice(self.donators) if self.donators else None
