import random
import typing
from dataclasses import dataclass

__all__ = (
    "DonatorQuotes",
    "Donator",
    "Donators",
)


@dataclass
class DonatorQuotes:
    """
    A dataclass containing all the quotes that can be said by a donator.

    Attributes
    ----------
    success : list[str]
        A list of quotes used when a user get's a reward. This will be formatted with the user's reward.
    failure : list[str]
        A list of quotes used when a user doesn't get a reward.

    Examples
    --------

    How the `success` attribute is formatted:

    >>> "You got {} for begging!"
    "You got **2x :alien: Alien** for begging!"

    """

    success: typing.List[str]
    fail: typing.List[str]


class Donator:
    """
    Represents a "donator". This is a person/character with it's own name, icon_url, and quotes.

    Attributes:
        name (`str`): The name of the donator.
        icon_url (`str`): The URL of the donator's icon. Square size recommended.
        quotes (`DonatorQuotes`): The quotes that can be said by the donator.
    """

    def __init__(
        self, name: str, *, icon_url: typing.Optional[str] = None, quotes: DonatorQuotes
    ):
        """
        Represents a "donator". This is a person/character with it's own name, icon_url, and quotes.

        Attributes:
            name (`str`): The name of the donator.
            icon_url (`str`): The URL of the donator's icon. Square size recommended.
            quotes (`DonatorQuotes`): The quotes that can be said by the donator.
        """

        self.name = name
        self.icon_url = icon_url
        self.quotes = quotes

    @classmethod
    def from_dict(cls, data: dict):
        """
        Creates a `Donator` from a dictionary.

        Args:
            data (`dict`): A dictionary containing the data to create the `Donator` from.

        Returns:
            `Donator`: The `Donator` created from the dictionary.
        """

        return cls(
            data["name"],
            icon_url=data.get("icon_url", None),
            quotes=DonatorQuotes(**data["quotes"]),
        )


@dataclass
class Donators:
    """
    Represents a list of `Donator`s.

    Attributes:
        donators (`list` of `Donator`): The list of `Donator`s.
    """

    donators: typing.List[Donator]

    def __init__(self, *donators: Donator):
        """
        Represents a list of `Donator`s.

        Args:
            donators (`list` of `Donator`): The list of `Donator`s.
        """

        self.donators = list(donators)

    @classmethod
    def from_dict(cls, data: dict):
        """
        Creates a `Donators` from a dictionary.

        Args:
            data (`dict`): A dictionary containing the data to create the `Donators` from.

        Returns:
            `Donators`: The `Donators` created from the dictionary.
        """

        return cls(
            *[Donator.from_dict(donator) for donator in data["donators"]],
        )

    def get_donator(self, name: str) -> typing.Union[Donator, None]:
        """
        Gets a `Donator` from the list of `Donator`s.

        Args:
            name (`str`): The name of the `Donator` to get.

        Returns:
            `Donator`: The `Donator` with the given name.
            or `None`: if no `Donator` with the given name exists.
        """

        return next((x for x in self.donators if x.name == name))

    def get_random_donator(self) -> typing.Union[Donator, None]:
        """
        Gets a random `Donator` from the list of `Donator`s.

        Returns:
            `Donator`: A random `Donator`.
            or `None`: if there are no `Donator`s in the list.
        """

        return random.choice(self.donators) if self.donators else None
