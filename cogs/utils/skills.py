import typing
from dataclasses import dataclass

import voxelbotutils as vbu


def get_level_by_exp(exp) -> int:
    """
    Returns the level of the player based on the amount of exp.
    """

    exp_per_level = [
        0,       50,     175,        # 1  2  3
        375,     675,    1_175,      # 4  5  6
        1_925,   2_925,  4_425,      # 7  8  9
        6_425,   9_925,  14_925,     # 10 11 12
        22_425,  32_425, 47_425,     # 13 14 15
        67_425,  97_425, 147_425,    # 16 17 18
        222_425, 322_425             # 19 20
    ]
    for n, i in enumerate(exp_per_level):
        if exp <= i:
            return n + 1

async def update_skill(db: vbu.DatabaseConnection, user_id: int, skill_name: str, experience: int):
    await db("""
        INSERT INTO user_skill VALUES ($1, $2, $3)
        ON CONFLICT (user_id, name) DO UPDATE SET experience = user_skill.experience + $3
        """, user_id, skill_name, experience
    )

class SkillWrapper: # Not as funny as PpWrapper

    def __init__(
        self, db: vbu.DatabaseConnection,
        user_id: int, update_values: typing.Optional[bool] = False
    ):
        self.db = db
        self.user_id = user_id
        self.update_values = update_values
    
    async def __aenter__(self):
        v = await self.db(
            """SELECT * FROM user_skill WHERE user_id = $1""",
            self.user_id
        )

        # If the user doesn't have a pp, create one
        if not v:
            self.skill = Skill(self.user_id)
        else:
            self.skill = Skill(**v[0])
        
        return self.skill
    
    async def __aexit__(self, *args):
        if self.update_values:
            await self.skill.update_values(self.db)


@dataclass
class Skill:
    user_id: int
    name: str
    experience: typing.Optional[int] = 0

    def __init__(
        self, user_id: int, name: typing.Optional[str] = 'Unnamed Pp',
        experience: typing.Optional[int] = 0
    ):
        self.user_id = user_id
        self.name = name
        self.experience = experience
    
    def __lt__(self, other):
        return self.size < other.size

    @property
    def level(self) -> int:
        return get_level_by_exp(self.experience)
    
    @classmethod
    def fetch(
        cls, db: vbu.DatabaseConnection, user_id: int,
        update_values: typing.Optional[bool] = True
    ):
        return SkillWrapper(db, user_id, update_values)

    async def update_values(self, db: vbu.DatabaseConnection):
        await db("""
            INSERT INTO user_pp VALUES ($1, $2, $3, $4) ON CONFLICT (user_id) DO UPDATE
            SET user_id = $1, name = $2, size = $3, multiplier = $4
            """, self.user_id, self.name, self.size, self.multiplier
        )