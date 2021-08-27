import random
import typing
import textwrap
from dataclasses import dataclass

import voxelbotutils as vbu
import discord

from cogs.utils import LootableItem
from cogs.utils.readable import int_formatting


@dataclass
class LootTableItem:
    """
    Class that represents a single item in a loot table.

    Attributes:
        id (`str` UPPER_SNAKE_CASE): The id of the item.
        drop_rate (`float`): The drop rate of the item.
        min (`int`): The minimum amount of the item that can be dropped.
        max (`int`): The maximum amount of the item that can be dropped.
    """

    id: str
    drop_rate: float
    min: int
    max: int


@dataclass
class LootTable:
    """
    A holder for :class:`LootTableItem`s

    Attributes:
        items (`list` of :class:`LootTableItem`): The items in the loot table.
    """

    items: typing.List[LootTableItem]

    def __init__(self, *items: LootTableItem):
        """
        Args:
            items (`list` of :class:`LootTableItem`): The items in the loot table.
        """
        self.items = list(items)


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
        id (`str` UPPER_SNAKE_CASE): (UPPER_SNAKE_CASE) The ID of the location.
        name (`str`): The name of the location. This will appeal as the label in a select menu.
        description (`str`): The description of the location. This will appear as the description in a select menu.
        emoji (`str` or `discord.Emoji`): The emoji that will be used to represent the location. Can also be a custom emoji.
        loot_table (`list` of :class:`LootTableItem`): The loot table for the location.
        quotes (:class:`Quotes`): The quotes for the location.
    """

    level: int
    id: str
    name: str
    description: str
    emoji: typing.Union[str, discord.Emoji]
    loot_table: typing.List[LootTableItem]
    quotes: Quotes

    def __init__(
        self, level: int, id: str, name: str, description: str,
        emoji: typing.Union[str, discord.Emoji], loot_table: typing.List[LootTableItem], quotes: Quotes,
    ):
        self.level = level
        self.id = id
        self.name = name
        self.description = description
        self.emoji = emoji
        self.loot_table = loot_table
        self.quotes = quotes

    @classmethod
    def from_dict(cls, bot: vbu.Bot, data: dict):
        """
        Loads an :class:`Item` from a dictionary. This can be used to load an item from `./config/items.toml`.

        Args:
            bot (:class:`voxelbot.VoxelBot`): The bot used for loading emojis.
            data (`dict`): The dictionary to load the item from.
        """

        return cls(
            data["level"],
            data["id"],
            data["name"],
            data["description"],
            bot.get_emoji(data["emoji"]) if isinstance(data["emoji"], int) else data["emoji"],
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

    @property
    def roman_numeral(self) -> str:
        """
        (`str`) The roman numeral representation of the level. E.g. "I" for level 1.
        """

        return int_formatting.int_to_roman(self.level)

    @property
    def label(self) -> str:
        """
        (`str`) The label of the location.
        
        E.g. "LEVEL IV: The park"
        """

        return f"LEVEL {self.roman_numeral}: {self.name}"

    def to_select_option(self) -> vbu.SelectOption:
        """
        Converts the location to a select option for the location menu.

        Returns:
            (:class:`vbu.SelectOption`): The select option for the location.
        """

        return vbu.SelectOption(
            label=self.label,
            value=self.id,
            description=self.description,
            custom_emoji=self.emoji,
        )

    def get_random_loot(self, bot: vbu.Bot, max_items: typing.Optional[int] = None) -> typing.List[LootableItem]:
        """
        Gets a random item from the loot table.

        Args:
            bot (:class:`vbu.Bot`): The bot which has the items cached.
            max_items (`int`): The maximum number of items to return. If None, all items will be returned.

        Returns:
            typing.List[:class:`LootableItem`]: The random items.
        """
        
        # The maximum number of items will be the length of the loot table, unless max_items is specified.
        if max_items is None:
            max_items = len(self.loot_table)
        
        # Create a list of :class:`LootableItem`s, which we'll be returning later.
        loot: typing.List[LootableItem] = []
        
        # Iterate over the loot table.
        for loot_table_item in self.loot_table:
            
            # Stop ourselves from going over the maximum number of items.
            if len(loot) >= max_items:
                break
            
            # Make a random check to see if we should add the item to the list.
            if random.random() <= loot_table_item.drop_rate:

                # Get the item from the cache.
                try:
                    item = bot.items['all'][loot_table_item.id]
                
                # If the item isn't in the cache, we'll raise an exception.
                except KeyError:

                    # Make a list of all possible causes for the exception.
                    possible_exception_causes = [
                        "{} isn't in the cache.",
                    ]

                    # If the cache doesn't contain the 'all' key, something is wrong.
                    if not bot.items.has_key('all'):
                        possible_exception_causes.append("Items not proporly cached, missing 'all' key in `bot.items`.")
                    
                    # Else, the item probably doesn't exist.
                    else:
                        possible_exception_causes.append("{} doesn't exist.")
                    
                    # Add the possible causes together, into a pretty string.
                    possible_exception_causes = "\n".join([f"- {i}" for i in possible_exception_causes])

                    # Now we format it with the item ID.
                    possible_exception_causes = possible_exception_causes.format(f'The item with the ID {loot_table_item.id}')

                    # Create a string containing the error message, which soon will be raised.
                    error_message = textwrap.dedent(
                        f"""Item '{loot_table_item.id}' not found in `bot.items` cache.
                        Possible causes:
                        {possible_exception_causes}"""
                    )

                    # Raise the exception with the `error_message`.
                    raise KeyError(error_message)

                # Generate a random number between the item's min and max.
                amount = random.randint(item.min, item.max)

                # Don't add the item if the amount is 0.
                if not amount:
                    continue

                # Create a new :class:`LootableItem` with the item and a random amount.
                lootable_item = LootableItem.from_item(
                    item,
                    amount,
                )

                # Add the :class:`LootableItem` to the list.
                loot.append(lootable_item)
        
        # Return the list of random :class:`LootableItem`s.
        return loot


@dataclass
class BeggingLocations:
    """
    A holder for :class:`BeggingLocation`s

    Attributes:
        locations (`dict`): A dictionary of locations.
    """

    level: int
    locations: typing.List[BeggingLocation]

    def __init__(self, level: int, *locations: BeggingLocation):
        """
        Args:
            *locations (:class:`BeggingLocation`): A list of the locations that this holder will hold.
        """
        self.level = level
        self.locations = list(location for location in locations if location.level <= self.level)
        self.locations.sort(key=lambda x: x.level, reverse=True)

    def add_location(self, location: BeggingLocation):
        """
        Adds a :class:`BeggingLocation` to this holder

        Args:
            location (:class:`BeggingLocation`): The location to add.
        """
        
        if not location.level > self.level:
            self.locations.append(location)
            self.locations.sort(key=lambda x: x.level, reverse=True)
        return self

    def remove_location(self, location: BeggingLocation):
        """
        Removes a :class:`BeggingLocation` to this holder

        Args:
            location (:class:`BeggingLocation`): The location to remove.
        """

        if not location.level > self.level:
            self.locations.remove(location)
            self.locations.sort(key=lambda x: x.level, reverse=True)
        return self

    def to_select_menu(self) -> vbu.SelectMenu:
        """
        Converts the locations to a select menu for the location menu.

        Returns:
            (:class:`vbu.SelectMenu`): The select menu for the locations with the ID of BEGGING_LOCATIONS.
        """

        return vbu.SelectMenu(
            custom_id="BEGGING_LOCATIONS",
            options=[i.to_select_option() for i in self.locations],
            placeholder="Pick a location to beg at.",
        )