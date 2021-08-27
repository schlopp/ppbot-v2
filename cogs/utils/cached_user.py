import typing
from dataclasses import dataclass

from cogs.utils import Pp, Skill

@dataclass
class CachedUser:
    """
    Represents a cached user.

    Attributes:
        user_id (int): The user's ID.
        skills (`list` of `:class:Pp`):  The user's cached skills.
        pp (`:class:Pp`):  The user's cached pp.
    """

    user_id: int
    skills: typing.List[Skill]
    pp: Pp

    def __init__(self, user_id: int, skills: typing.List[Skill], pp: Pp):
        """
        Represents a cached user.

        Args:
            user_id (int): The user's ID.
            skills (`list` of `:class:Pp`):  The user's cached skills.
            pp (`:class:Pp`):  The user's cached pp.
        """

        self.user_id = user_id
        self.skills = skills
        self.pp = pp
    
    def get_skill(self, skill_id: str) -> Skill:
        """
        Gets a skill

        Args:
            skill_id (`str`):  The skill's id.

        Returns:
            `:class:Skill`:  The skill.
            or `Skill`:  An empty skill with the skill_id.
        """

        # return the skill if it exists
        for skill in self.skills:
            if skill.id == skill_id:
                return skill
        return Skill(self.user_id, name=skill_id)
