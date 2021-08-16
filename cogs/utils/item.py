import typing
from dataclasses import dataclass


@dataclass
class SkillRequirements:
    id: str
    level: int

@dataclass
class ShopSettings:
    buyable: bool
    buy: int
    sell: int
    auctionable: bool

@dataclass
class Recipe:
    id: str
    amount: int

@dataclass
class CraftingUsage:
    id: str
    amount: int

@dataclass
class BrewingUsage:
    id: str
    amount: int

@dataclass
class SkillUsage:
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