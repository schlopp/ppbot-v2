import typing
from json import loads as jsonloads, dumps as jsondumps


class Dict(dict):
    """
    Modified dict
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    @classmethod
    def from_json(cls, json: str):
        return cls(jsonloads(json))

    def to_json(self) -> str:
        return jsondumps(self)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return 0

    def __delitem__(self, key):
        try:
            return super().__delitem__(key)
        except KeyError:
            pass
