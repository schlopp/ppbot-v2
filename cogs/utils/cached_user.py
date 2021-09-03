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

    def get_skill(self, name: str) -> Skill:
        """
        Gets a skill

        Args:
            name (`str`):  The skill's name.

        Returns:
            `:class:Skill`:  The skill.
            or `Skill`:  An empty skill with `name` as the skill name.
        """

        skill = next((x for x in self.skills if x.name == name), None)
        if skill is None:
            skill = Skill(self.user_id, name=name)
            self.skills.append(skill)
            return skill
        return skill
