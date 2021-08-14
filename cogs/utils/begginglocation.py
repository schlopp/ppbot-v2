import typing
import itertools
from dataclasses import dataclass

import voxelbotutils as vbu
import toml

from cogs.utils.readable import roman_numeral


class Base:
    QUOTES = toml.load('config/begging.toml')['quotes']['failure']

@dataclass(init=False, order=True)
class BeggingLocation:
    level: int
    id: str
    emoji: str
    name: str
    description: str
    quotes: list

    def __init__(self, level: int, id: str, emoji: str, name: str, description: str, quotes: typing.Dict[str, dict]):
        self.level = level
        self.id = f'{self.level}-{id}'
        self.emoji = emoji
        self.name = name
        self.description = description
        self.quotes = quotes
        base_quotes_copy = Base.QUOTES.copy()
        base_quotes_copy.append(quotes)
        self.quotes['fail'] = base_quotes_copy

    def to_selectoption(self):
        return vbu.SelectOption(f'LEVEL {roman_numeral(self.level)}: {self.name}', self.id, description=self.description, emoji=self.emoji, default=False)

@dataclass(init=False)
class BeggingLocations:
    level: int
    locations: typing.List[BeggingLocation]

    def __init__(self, level: int, *locations: typing.Iterable[BeggingLocation]):
        self.level = level
        self.locations = sorted([i for i in locations if i.level <= level], key=lambda x: x.level, reverse=True)

    @property
    def quotes(self):
        """
        Returns a list of quotes for each location with the base quotes appended to it.
        """
        l = [i.quotes['fail'] for i in self.locations]
        l.append(Base.QUOTES)
        return list(itertools.chain.from_iterable(l))

    def to_selectmenu(self):
        return vbu.SelectMenu('SELECT_LOCATION', [i.to_selectoption() for i in self.locations], 'Select a location.', 1, 1,)
