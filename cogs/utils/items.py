import typing
from json import loads as jsonloads
import voxelbotutils as vbu


class Requirement:
    """
    # Requirement
    ## attributes:
    - `id:str` requirement ID. Example: `"FISHING"`
    - `value:int` value of the requirement needed. Example: `100`
    """

    FISHING = 'FISHING'
    HUNTING = 'HUNTING'

    def __init__(self, name:str, value:int):
        self.name = name
        self.value = value
    
    def to_dict(self) -> dict:
        return {self.name: self.value}

class Requirements:
    """
    Support __init__, from_json, __eq__ and __ne__
    """
    def __init__(self, *requirements:typing.Optional[typing.List[Requirement]]):
        for i in requirements:
            setattr(self, i.name, i.value)
    
    @classmethod
    def from_json(cls, json:str):
        for name, value in jsonloads(json):
            self.name = value

    def __eq__(self, value):
        try:
            return True if self.__dict__ == value.__dict__ else False
        except:
            return False
    
    def __ne__(self, value):
        return not self.__eq__(value)
    
    def __format__(self, format_spec):
        for key, value in self.__dict__.items():
            print(key, value)
        return str(id(self))
        #return "<Requirements {0}>".format('{0["name"]}'.format(self.__dict__))



rql = Requirements(Requirement(Requirement.FISHING, 11))
rql2 = Requirements(Requirement(Requirement.FISHING, 11))
print(f'{rql}')