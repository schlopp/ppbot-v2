import typing
from dataclasses import dataclass


@dataclass
class LootTableItem:
    """
    Class that represents a single item in a loot table.

    Attributes:
        id (`str`): The id of the item (UPPER_SNAKE_CASE).
        weight (`int`): The weight of the item in the loot table. A higher weight means the item will be more likely to be chosen or chosen multiple times.
        limit (`int`): The maximum number of this item that can be dropped from the parent :class:BeggingLocation.
    """

    id: str
    weight: float
    limit: int


@dataclass
class FillInTheBlank:
    """
    Class that represents the fill-in-the-blank mini-game for :class:MiniGames.

    Attributes:
        approacher (`str`): The person approaching the user in this mini-game.
        context (`str`): The context of the mini-game.
        success (`str`): The success message for the user. E.g. "gameshow host: 'Good job! You win!'"
        fail (`str`): The failure message for the user. E.g. "gameshow host: 'Sorry, you lose!'"
    """

    approacher: str
    context: str
    success: str
    fail: str


@dataclass
class MiniGames:
    """
    Class that represents the mini-games for a :class:BeggingLocation.

    Attributes:
        fill_in_the_blank (:class:`FillInTheBlank`): The fill-in-the-blank minigame
    """

    fill_in_the_blank: FillInTheBlank


@dataclass
class Quotes:
    """
    Class that represents the quotes for a :class:BeggingLocation.

    Attributes:
        success (`str`): The success message for the user. E.g. "gameshow host: 'Good job! You win!'" This will be formatted, so you can use {0} to represent the reward.

        fail (`str`): The failure message for the user. E.g. "gameshow host: 'Sorry, you lose!'"
        minigames (:class:`MiniGames`): The mini-games for the user to complete.
    """

    success: typing.List[str]
    fail: typing.List[str]
    minigames: MiniGames

@dataclass
class BeggingLocation:
    """
    Represents a begging location for the beg command.

    Attributes:
        level (`int`): The level of the location. This will determine if a user is allowed to use the location. Example: A user with Begging level 0 can't use a level 1 location.
        id (`str`): (UPPER_SNAKE_CASE) The ID of the location.
        name (`str`): The name of the location. This will appeal as the label in a select menu.
        description (`str`): The description of the location. This will appear as the description in a select menu.
        emoji (`str`): The emoji that will be used to represent the location. Can also be custom disco emoji, E.g. "<custom_emoji:123456789>"
        loot_table (`list` of :class:`LootTableItem`): The loot table for the location.
        quotes (:class:`Quotes`): The quotes for the location.
    """

    level: int
    id: str
    name: str
    description: str
    emoji: str
    loot_table: typing.List[LootTableItem]
    quotes: Quotes

    def __init__(
        self, level: int, id: str, name: str, description: str,
        emoji: str, loot_table: typing.List[LootTableItem], quotes: Quotes,
    ):
        self.level = level
        self.id = id
        self.name = name
        self.description = description
        self.emoji = emoji
        self.loot_table = loot_table
        self.quotes = quotes
    
    @classmethod
    def from_dict(cls, data: dict):
        """
        Loads an :class:`Item` from a dictionary. This can be used to load an item from `./config/items.toml`.

        Args:
            data (`dict`): The dictionary to load the item from.
        """

        return cls(
            data["level"],
            data["id"],
            data["name"],
            data["description"],
            data["emoji"],
            [
                LootTableItem(**item) for item in data["loot_table"]
            ],
            Quotes(
                data["quotes"]["success"],
                data["quotes"]["fail"],
                MiniGames(
                    FillInTheBlank(
                        **data["quotes"]["minigames"]["fill_in_the_blank"],
                    ),
                ),
            ),
        )

@dataclass
class BeggingLocations:
    """
    A holder for :class:`BeggingLocation`s

    Attributes:
        locations (`dict`): A dictionary of locations.
    """

    locations: typing.List[BeggingLocation]

    def __init__(self, *locations: BeggingLocation):
        """
        Args:
            *locations (:class:`BeggingLocation`): A list of the locations that this holder will hold.
        """
        self.locations = list(locations)
    
    def add_location(self, location: BeggingLocation):
        """
        Adds a :class:`BeggingLocation` to this holder

        Args:
            location (:class:`BeggingLocation`): The location to add.
        """

        self.locations.append(location)
        return self
    
    def remove_location(self, location: BeggingLocation):
        """
        Removes a :class:`BeggingLocation` to this holder

        Args:
            location (:class:`BeggingLocation`): The location to remove.
        """

        self.locations.remove(location)
        return self
