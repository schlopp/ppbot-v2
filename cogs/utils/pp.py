import typing

import voxelbotutils as vbu
from dataclasses import dataclass


class PpWrapper:  # haha condom

    def __init__(self, db: vbu.DatabaseConnection, user_id: int, update: typing.Optional[bool] = True):
        self.db = db
        self.user_id = user_id
        self.update = update

    async def __aenter__(self):
        v = await self.db("""SELECT * FROM user_pp WHERE user_id=$1""", self.user_id)
        if not v:
            self.pp = Pp(self.user_id)
        else: 
            self.pp = Pp(**v[0])
        return self.pp

    async def __aexit__(self, *args):
        if self.update:
            await self.pp.update(self.db)


@dataclass(init=True, repr=True, eq=True, order=True, unsafe_hash=False, frozen=False)
class Pp:
    user_id: int
    name: typing.Optional[str] = 'Unnamed Pp'
    size: typing.Optional[int] = 0
    multiplier: typing.Optional[float] = 1.0

    def __init__(
            self, user_id: int, name: typing.Optional[str] = 'Unnamed Pp',
            size: typing.Optional[int] = 0, multiplier: typing.Optional[float] = 1.0):
        self.user_id = user_id
        self.name = name
        self.size = size
        self.multiplier = multiplier

    @classmethod
    def fetch(cls, db: vbu.DatabaseConnection, user_id: int, update: typing.Optional[bool] = True):
        return PpWrapper(db, user_id, update)
    
    async def update(self, db: vbu.DatabaseConnection):
        await db("""
            INSERT INTO user_pp VALUES ($1, $2, $3, $4) ON CONFLICT (user_id) DO UPDATE
            SET user_id = $1, name = $2, size = $3, multiplier = $4""",
            self.user_id, self.name, self.size, self.multiplier)
