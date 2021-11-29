import typing
from dataclasses import dataclass

import discord
from discord.ext import vbu

__all__ = (
    "SkillRequirements",
    "ShopSettings",
    "Recipe",
    "CraftingUsage",
    "BrewingUsage",
    "SkillUsage",
    "Usage",
    "Item",
    "LootableItem",
)


@dataclass
class SkillRequirements:
    """
    Represents a skill requirement for a given item.

    Attributes:
        id (`str` UPPER_SNAKE_CASE): The ID of the required skill.
        level (`int`): The level of the required skill.
    """

    id: str
    level: int


@dataclass
class ShopSettings:
    """
    Represents a shop settings. I.e. the price, if it's buyable, if it's auctionable, etc.

    Attributes:
        buyable (`bool`): Whether the item can be bought from the shop.
        buy (`int`): The price of the item when bought from the shop.
        sell (`int`): The price of the item when sold to the shop.
        auctionable (`bool`): Whether the item can be put up for auction.
    """

    auctionable: bool
    buyable: bool
    buy: int
    sell: int


@dataclass
class Recipe:
    """
    Represents a recipes of an item

    Attributes:
        id (`str` UPPER_SNAKE_CASE): The ID of an item that is required to craft the parent item.
        amount (`int`): The amount of the parent item required to craft said item.
    """

    id: str
    amount: int


@dataclass
class CraftingUsage:
    """
    Represents a crafting recipe involving the parent item.

    Attributes:
        id (`str` UPPER_SNAKE_CASE): The ID of an item craftable with the parent item.
        amount (`int`): The amount of the parent item required to craft said item.
    """

    id: str
    amount: int


@dataclass
class BrewingUsage:
    """
    Represents a brewing recipe involving the parent item.

    Attributes:
        id (`str` UPPER_SNAKE_CASE): The ID of a potion or beverage craftable with the parent item.
        amount (`int`): The amount of the parent item required to brew said potion or beverage.
    """

    id: str
    amount: int


@dataclass
class SkillUsage:
    """
    Represents a skill requirement for the parent item.

    atrributes:
        id (`str` UPPER_SNAKE_CASE): The ID of the skill that the parent item is used for.
    """

    id: str


@dataclass
class Usage:
    """
    Represents the usage of an item.

    Attributes:
        crafting (`list` of :class:`CraftingUsage`): A list of crafting recipes involving the parent item.
        brewing (`list` of :class:`BrewingUsage`): A list of brewing recipes involving the parent item.
        skill (`list` of :class:`SkillUsage`): A list of the skill requirements for the parent item.
    """

    crafting: typing.List[CraftingUsage]
    brewing: typing.List[BrewingUsage]
    skill: typing.List[SkillUsage]

    @classmethod
    def from_dict(cls, data: dict):
        """
        Loads a :class:`Usage` from a dictionary.

        Args:
            data (`dict`): The dictionary to load the :class:`Usage` from.
        """

        return cls(
            [CraftingUsage(**c) for c in data["crafting"] if c],
            [BrewingUsage(**b) for b in data["brewing"] if b],
            [SkillUsage(**s) for s in data["skills"] if s],
        )


@dataclass
class Item:
    """
    Represents an item.

    Attributes:
        id (`str` UPPER_SNAKE_CASE): The ID of the item.
        type (`str` UPPER_SNAKE_CASE): The type of the item.
        rarity (`str` UPPER_SNAKE_CASE): The rarity of the item.
        emoji (`int` or `str`): The custom ID of the emoji associated with the item.
        name (`str`): The name of the item.
        description (`str`): The description of the item.
        skill_requirements (`list` of :class:`SkillRequirements`): The skill requirements of the item.
        shop_settings (`list` of :class:`ShopSettings`): The shop settings of the item.
        recipe (`list` of :class:`Recipe`): The recipe of the item.
        usage (:class:`Usage`): The usage of the item.
    """

    id: str
    type: str
    rarity: str
    emoji: int
    name: str
    description: str
    skill_requirements: typing.List[SkillRequirements]
    shop_settings: ShopSettings
    recipe: typing.List[Recipe]
    usage: Usage

    def __init__(
        self,
        bot: vbu.Bot,
        id: str,
        type: str,
        rarity: str,
        emoji: int,
        name: str,
        description: str,
        skill_requirements: typing.List[SkillRequirements],
        shop_settings: ShopSettings,
        recipe: typing.List[Recipe],
        usage: Usage,
    ):
        """
        Args:
            id (`str` UPPER_SNAKE_CASE): The ID of the item.
            type (`str` UPPER_SNAKE_CASE): The type of the item..
            rarity (`str` UPPER_SNAKE_CASE): The rarity of the item.
            emoji (`int` or `str`): The custom ID of the emoji associated with the item.
            name (`str`): The name of the item.
            description (`str`): The description of the item.
            skill_requirements (`list` of :class:`SkillRequirements`): The skill requirements of the item.
            shop_settings (`list` of :class:`ShopSettings`): The shop settings of the item.
            recipe (`list` of :class:`Recipe`): The recipe of the item.
            usage (:class:`Usage`): The usage of the item.
            amount (`int`): The amount of the item.
        """
        self.id = id
        self.type = type
        self.rarity = rarity
        self.emoji = bot.get_emoji(emoji) if isinstance(emoji, int) else emoji
        self.name = name
        self.description = description
        self.skill_requirements = skill_requirements
        self.shop_settings = shop_settings
        self.recipe = recipe
        self.usage = usage

    @classmethod
    def from_dict(cls, bot: vbu.Bot, data: dict):
        """
        Loads an :class:`Item` from a dictionary. This can be used to load an item from `./config/items.toml`.

        Args:
            data (`dict`): The dictionary to load the item from.
        """

        return cls(
            bot,
            data["id"],
            data["type"],
            data["rarity"],
            bot.get_emoji(data["emoji"])
            if isinstance(data["emoji"], int)
            else data["emoji"],
            data["name"],
            data["description"],
            [SkillRequirements(**req) for req in data["skill_requirements"] if req],
            ShopSettings(**data["shop_settings"]),
            [Recipe(**r) for r in data["recipe"] if r],
            Usage.from_dict(data["usage"]),
        )


@dataclass
class LootableItem(Item):
    """
    An item that can be looted, given, received, etc.

    Attributes:
        id (`str` UPPER_SNAKE_CASE): The ID of the item.
        type (`str` UPPER_SNAKE_CASE): The type of the item..
        rarity (`str` UPPER_SNAKE_CASE): The rarity of the item.
        emoji (`int` or `str`): The custom ID of the emoji associated with the item.
        name (`str`): The name of the item.
        description (`str`): The description of the item.
        skill_requirements (`list` of :class:`SkillRequirements`): The skill requirements of the item.
        shop_settings (`list` of :class:`ShopSettings`): The shop settings of the item.
        recipe (`list` of :class:`Recipe`): The recipe of the item.
        usage (:class:`Usage`): The usage of the item.
        amount (`int`): The amount of the item.
    """

    amount: int = 1

    def __init__(
        self,
        bot: vbu.Bot,
        id: str,
        type: str,
        rarity: str,
        emoji: typing.Union[int, discord.Emoji],
        name: str,
        description: str,
        skill_requirements: typing.List[SkillRequirements],
        shop_settings: ShopSettings,
        recipe: typing.List[Recipe],
        usage: Usage,
        amount: int = 1,
    ):
        """
        Args:
            bot (:class:`vbu.Bot`): The bot.
            id (`str` UPPER_SNAKE_CASE): The ID of the item.
            type (`str` UPPER_SNAKE_CASE): The type of the item..
            rarity (`str` UPPER_SNAKE_CASE): The rarity of the item.
            emoji (`int` or `str`): The custom ID of the emoji associated with the item.
            name (`str`): The name of the item.
            description (`str`): The description of the item.
            skill_requirements (`list` of :class:`SkillRequirements`): The skill requirements of the item.
            shop_settings (`list` of :class:`ShopSettings`): The shop settings of the item.
            recipe (`list` of :class:`Recipe`): The recipe of the item.
            usage (:class:`Usage`): The usage of the item.
            amount (`int`): The amount of the item.
        """

        self.id = id
        self.type = type
        self.rarity = rarity
        self.emoji = bot.get_emoji(emoji) if isinstance(emoji, int) else emoji
        self.name = name
        self.description = description
        self.skill_requirements = skill_requirements
        self.shop_settings = shop_settings
        self.recipe = recipe
        self.usage = usage
        self.amount = amount

    @classmethod
    def from_item(cls, bot: vbu.Bot, item: Item, amount: int):
        """
        Loads a :class:`LootableItem` from an :class:`Item`.

        Args:
            item (:class:`Item`): The item to load from.
            amount (`int`): The amount of the item.
        """

        return cls(
            bot,
            item.id,
            item.type,
            item.rarity,
            item.emoji,
            item.name,
            item.description,
            item.skill_requirements,
            item.shop_settings,
            item.recipe,
            item.usage,
            amount,
        )
