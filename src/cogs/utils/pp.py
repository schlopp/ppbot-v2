import typing
from dataclasses import dataclass

from discord.ext import vbu  # type: ignore

__all__ = ("Pp",)


class PpWrapper:  # Haha, condom
    def __init__(
        self,
        db: vbu.DatabaseConnection,
        user_id: int,
        update_values: typing.Optional[bool] = False,
    ):
        self.db = db
        self.user_id = user_id
        self.update_values = update_values

    async def __aenter__(self):
        v = await self.db("""SELECT * FROM user_pp WHERE user_id = $1""", self.user_id)

        # If the user doesn't have a pp, create one
        if not v:
            self.pp = Pp(self.user_id)
        else:
            self.pp = Pp(**v[0])

        return self.pp

    async def __aexit__(self, *args):
        if self.update_values:
            await self.pp.update_values(self.db)


@dataclass
class Pp:
    user_id: int
    name: str = "Unnamed Pp"
    size: int = 0
    multiplier: float = 1.0

    def __lt__(self, other):
        return self.size < other.size

    @classmethod
    def fetch(
        cls,
        db: vbu.DatabaseConnection,
        user_id: int,
        update_values: typing.Optional[bool] = True,
    ):
        return PpWrapper(db, user_id, update_values)

    async def update_values(self, db: vbu.DatabaseConnection):
        await db(
            """
            INSERT INTO user_pp VALUES ($1, $2, $3, $4) ON CONFLICT (user_id) DO UPDATE
            SET user_id = $1, name = $2, size = $3, multiplier = $4
            """,
            self.user_id,
            self.name,
            self.size,
            self.multiplier,
        )
