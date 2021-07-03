import typing
import voxelbotutils as vbu
from dataclasses import dataclass


@dataclass(init=True, repr=True, eq=True, order=True, unsafe_hash=False, frozen=False)
class Pp:
    user_id: int
    name: typing.Optional[str] = 'Unnamed Pp'
    amount: typing.Optional[int] = 0
    multiplier: typing.Optional[float] = 1.0

    def __init__(
        self, user_id: int, name: typing.Optional[str] = 'Unnamed Pp',
        amount: typing.Optional[int] = 0, multiplier: typing.Optional[float] = 1.0,
    ):
        self.user_id = user_id
        self.name = name
        self.amount = amount
        self.multiplier = multiplier


pp = Pp(1)
print(pp)
