import typing
import discord
import asyncpg
import voxelbotutils as vbu
from json import dumps as jsondumps
from json import loads as jsonloads
from cogs.utils import Dict


class Lore:
    """
    Lore
    """

    def __init__(self, description:str, story:typing.List[str]):
        self.description = description
        self.story = story

    def __repr__(self):
        return f'<Lore description="{self.description}", story={self.story}>'
    
    @classmethod
    def from_json(cls, json:str):
        json = jsonloads(json)
        return cls(json['description'], json['story'])

    def to_dict(self) -> dict:
        return {
            'description': self.description,
            'story': self.story,
        }
    
    def to_json(self) -> str:
        return jsondumps(self.to_dict())

class ShopSettings:
    """
    Shop settings
    """

    def __init__(self, for_sale:bool, buy:typing.Optional[int]=0, sell:typing.Optional[int]=0):
        self.for_sale = for_sale
        self.buy = buy
        self.sell = sell

    def __repr__(self):
        return f'<ShopSettings for_sale={self.for_sale}, buy={self.buy}, sell={self.sell}>'
    
    @classmethod
    def from_json(cls, json:str):
        json = jsonloads(json)
        return cls(json['for_sale'], buy=json['buy'], sell=json['sell'])

    def to_dict(self) -> dict:
        return {
            'for_sale': self.for_sale,
            'buy': self.buy,
            'sell': self.sell,
        }

    def to_json(self) -> str:
        return jsondumps(self.to_dict())

class Item:
    """
    :class:`Item`
    """

    def __init__(
                self, name:str, *, requires:typing.Optional[Dict]=Dict({}), type:str, shopsettings:ShopSettings,
                rarity:str, auctionable:bool, emoji:str,
                recipe:typing.Optional[Dict]=Dict({}), used_for:typing.Optional[typing.List[str]]=Dict({}),
                recipes:typing.Optional[Dict]=Dict({}), buffs:typing.Optional[typing.List[Dict]]=[], lore:Lore,
                amount:typing.Optional[int]=None):
        self.name = name
        self.requires = requires
        self.shopsettings = shopsettings
        self.recipe = recipe
        self.type = type
        self.rarity = rarity
        self.auctionable = auctionable
        self.emoji = emoji
        self.used_for = used_for
        self.recipes = recipes
        self.buffs = buffs
        self.lore = lore
        self.amount = amount
    
    def __repr__(self):
        variables = [f'{k}=\'{v}\'' if isinstance(v, str) else f'{k}={v}' for k, v in vars(self).items()]
        return '<Item {}>'.format(', '.join(variables))

    @classmethod
    def from_record(cls, record:asyncpg.Record):
        return cls(
            record['name'],
            requires=Dict.from_json(record['requires']),
            type=record['type'],
            shopsettings=ShopSettings(record['shop_for_sale'], record['shop_buy'], record['shop_sell']),
            rarity=record['rarity'],
            auctionable=record['auctionable'],
            emoji=record['emoji'],
            recipe=Dict.from_json(record['recipe']),
            used_for=record['used_for'],
            recipes=Dict.from_json(record['recipes']),
            buffs=[Dict.from_json(i) for i in record['buffs']],
            lore=Lore(
                record['description'],
                record['story'],
            ),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "requires": self.requires,
            "shop_for_sale": self.shopsettings.for_sale,
            "shop_buy": self.shopsettings.buy,
            "shop_sell": self.shopsettings.sell,
            "recipe": self.recipe,
            "type": self.type,
            "rarity": self.rarity,
            "auctionable": self.auctionable,
            "emoji": self.emoji,
            "used_for": self.used_for,
            "recipes": self.recipes,
            "buffs": self.buffs,
            "lore": self.lore.to_json(),
            "amount": self.amount,
        }
    
    def to_json(self) -> str:
        return jsondumps(self.to_dict())

    async def create(self, db:vbu.DatabaseConnection):
        buffs = self.buffs if self.buffs is None else []
        await db('''
            INSERT INTO items
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            ON CONFLICT (name) DO NOTHING;''',
            self.name, self.requires.to_json(), self.type,
            self.rarity, self.auctionable, self.lore.description,
            self.emoji, self.used_for, self.recipe.to_json(),
            self.recipes.to_json(), buffs, self.shopsettings.for_sale,
            self.shopsettings.buy, self.shopsettings.sell,
            self.lore.story
            )
