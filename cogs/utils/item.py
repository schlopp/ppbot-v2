import typing
from dataclasses import dataclass


@dataclass
class SkillRequirements:
    """
    Represents the requirements for a skill.

    Attributes:
        id (`str`): The ID of the skill required. (UPPER_SNAKE_CASE).
        level (`int`): The level of the skill required.
    """

    id: str
    level: int

@dataclass
class ShopSettings:
    """
    Represents the shop settings. I.e. the price, if it's buyable, if it's auctionable, etc.
    
    Attributes:
        buyable (`bool`): Whether the item can be bought from the shop.
        buy (`int`): The price of the item when bought from the shop.
        sell (`int`): The price of the item when sold to the shop.
    """

    buyable: bool
    buy: int
    sell: int
    auctionable: bool

@dataclass
class Recipe:
    """
    Represents the recipes of an item

    Attributes:
        id (`str`): The ID of an item that is required to craft the parent item (UPPER_SNAKE_CASE).
        amount (`int`): The amount of the parent item required to craft said item.
    """

    id: str
    amount: int

@dataclass
class CraftingUsage:
    """
    Represents the crafting recipe involving the parent item.

    Attributes:
        id (`str`): The ID of an item craftable with the parent item (UPPER_SNAKE_CASE).
        amount (`int`): The amount of the parent item required to craft said item.
    """

    id: str
    amount: int

@dataclass
class BrewingUsage:
    """
    Represents the brewing recipe involving the parent item.

    Attributes:
        id (`str`): The ID of a potion or beverage craftable with the parent item (UPPER_SNAKE_CASE).
        amount (`int`): The amount of the item required to brew said potion or beverage (int).
    """

    id: str
    amount: int

@dataclass
class SkillUsage:
    """
    Represents a skill that the parent item is used for.

    atrributes:
        id (`str`): The ID of the skill that the parent item is used for (UPPER_SNAKE_CASE).
    """
    id: str

@dataclass
class Usage:
    crafting: typing.List[CraftingUsage]
    brewing: typing.List[BrewingUsage]
    skill: typing.List[SkillUsage]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            [CraftingUsage(**c) for c in data['crafting'] if c],
            [BrewingUsage(**b) for b in data['brewing'] if b],
            [SkillUsage(**s) for s in data['skills'] if s],
        )

@dataclass
class Item:
    id: str
    type: str
    rarity: str
    emoji: typing.Union[int, str]
    name: str
    description: str
    skill_requirements: typing.List[SkillRequirements]
    shop_settings: ShopSettings
    recipe: typing.List[Recipe]
    usage: Usage

    def __init__(
        self, id: str, type: str, rarity: str, emoji: typing.Union[int, str],
        name: str, description: str, skill_requirements: typing.List[SkillRequirements],
        shop_settings: ShopSettings, recipe: typing.List[Recipe],usage: Usage,
    ):
        self.id = id
        self.type = type
        self.rarity = rarity
        self.emoji = emoji
        self.name = name
        self.description = description
        self.skill_requirements = skill_requirements
        self.shop_settings = shop_settings
        self.recipe = recipe
        self.usage = usage
    
    @classmethod
    def from_dict(cls, data):
        """
        Loads an Item from a dict.
        """

        return cls(
            data['id'],
            data['type'],
            data['rarity'],
            data['emoji'],
            data['name'],
            data['description'],
            [SkillRequirements(**req) for req in data['skill_requirements'] if req],
            ShopSettings(**data['shop_settings']),
            [Recipe(**r) for r in data['recipe'] if r],
            Usage.from_dict(data['usage']),
        )