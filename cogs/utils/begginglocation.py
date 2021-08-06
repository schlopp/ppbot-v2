import typing
import itertools
from dataclasses import dataclass

import voxelbotutils as vbu
import toml

from cogs.utils.readable import int_to_roman


class Base:
    QUOTES = toml.load('config/begging.toml')['quotes']['failure']

@dataclass(init=False, order=True)
class BeggingLocation:
    level: int
    id: str
    emoji: str
    name: str
    description: str
    specific_quotes: typing.List[str]

    def __init__(self, level: int, id: str, emoji: str, name: str, description: str, specific_quotes: typing.List[str]):
        self.level = level
        self.id = f'{self.level}-{id}'
        self.emoji = emoji
        self.name = name
        self.description = description
        self.specific_quotes = specific_quotes
    
    @property
    def quotes(self):
        l = Base.QUOTES.copy()
        l.append(self.specific_quotes)
        return l
    
    def to_selectoption(self):
        return vbu.SelectOption(f'LVL {int_to_roman(self.level)}: {self.name}', self.id, description=self.description, emoji=self.emoji, default=False)

@dataclass(init=False)
class BeggingLocations:
    level: int
    locations: typing.List[BeggingLocation]

    def __init__(self, level: int, *locations: typing.Iterable[BeggingLocation]):
        self.level = level
        self.locations = sorted([i for i in locations if i.level <= level], key=lambda x: x.level, reverse=True)
    
    def quotes(self):
        l = Base.QUOTES.copy()
        l.append([i.specific_quotes for i in self.locations])
        return list(itertools.chain.from_iterable(l))

    def to_selectmenu(self):
        return vbu.SelectMenu('SELECT_LOCATION', [i.to_selectoption() for i in self.locations], 'Select a location.', 1, 1,)
