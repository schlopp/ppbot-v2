import typing

import voxelbotutils as vbu
from dataclasses import dataclass


class PpWrapper:  # haha condom

    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id

    async def __aenter__(self):
        v = await self.db("""SELECT * FROM user_pp WHERE user_id=$1""", self.id)
        return Pp(**v[0])

    async def __aexit__(self, *args):
        await self.update()


@dataclass(init=True, repr=True, eq=True, order=True, unsafe_hash=False, frozen=False)
class Pp:
    user_id: int
    name: typing.Optional[str] = 'Unnamed Pp'
    amount: typing.Optional[int] = 0
    multiplier: typing.Optional[float] = 1.0

    def __init__(
            self, user_id: int, name: typing.Optional[str] = 'Unnamed Pp',
            amount: typing.Optional[int] = 0, multiplier: typing.Optional[float] = 1.0):
        self.user_id = user_id
        self.name = name
        self.amount = amount
        self.multiplier = multiplier

    @classmethod
    def fetch(cls, db, id):
        return PpWrapper(db, id)
    
    async def update(self):
        await self.db("""
            INSERT INTO user_pp VALUES ($1, $2, $3, $4) ON CONFLICT (user_id) DO UPDATE
            SET user_id = $1, name = $2, amount = $3, multiplier = $4""",
            self.user_id, self.name, self.amount, self.multiplier)
