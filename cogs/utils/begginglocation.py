import typing
import itertools
from dataclasses import dataclass

import voxelbotutils as vbu

from cogs.utils.readable import int_to_roman


class Base:
    QUOTES = [
            'Ew poor person, step away from me please. I need to wash my hands now',
            'Don\'t touch my pp you freak, what do think you\'re doing???',
            'My wife has a bigger pp than you I\'m not giving you shit',
            'I\'m not donating to someone with such a tiny pp oh my god please go away',
            'Cringe tiny pp',
            'beg harder daddy',
            'People with a small pp make me scared',
            'Don\'t touch me poor person',
            'Get a job',
            'Oh my.. Did you really just beg for my pp? I\'m offended', 
            'No you',
            'I don\'t speak poor',
            'You should take a shower',
            'I love my wife... I love my wife... I love my wife..',
            'Hey, it\'s important to stay hydrated. Drink some water mate, love you',
            'Begone beggar',
            'No.',
            'Oh hell nah I\'m not giving you my inches',
            'Try being a little "cooler" next time',
            'Get the fuck out of my sight',
            'I\'m not giving you anything mate',
        ]

@dataclass
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
    
    def __lt__(self, other):
        return self.level < other.level
    
    @property
    def quotes(self):
        l = Base.QUOTES.copy()
        l.append(self.specific_quotes)
        return l
    
    def to_selectoption(self):
        return vbu.SelectOption(f'LVL {int_to_roman(self.level)}: {self.name}', self.id, description=self.description, emoji=self.emoji, default=False)

@dataclass
class BeggingLocations:
    locations: typing.Iterable[BeggingLocation]
    quotes: typing.List[str]

    def __init__(self, *locations: typing.Iterable[BeggingLocation]):
        self.locations = locations
    
    @property
    def quotes(self):
        l = Base.QUOTES.copy()
        l.append([i.specific_quotes for i in self.locations])
        return list(itertools.chain.from_iterable(l))

    def to_selectmenu(self):
        return vbu.SelectMenu('SELECT_LOCATION', [i.to_selectoption() for i in self.locations], 'Select a location.', 1, 1,)