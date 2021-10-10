import typing
from dataclasses import dataclass

from discord.ext import vbu

from . import Pp, Skill


__all__ = ("CachedUser", "get_user_cache")


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

        try:
            skill = next(x for x in self.skills if x.name == name)
        except StopIteration:
            skill = None
        if skill is None:
            skill = Skill(self.user_id, name=name)
            self.skills.append(skill)
            return skill
        return skill


async def get_user_cache(
    cog: vbu.Cog, user_id: int, db: typing.Optional[vbu.DatabaseConnection]
) -> CachedUser:
    """
    Returns user's cached information, if any. Otherwise returns data from the database.

    Args:
        cog (`:class:vbu.Cog`):  The cog.
        user_id (`int`): The user's ID.
        db (:class:`voxelbotutils.DatabaseConnection`): The database connection.

    Returns:
        :class:`UserCache`: The user's cache.
    """

    # If the user is already cached, return it
    try:
        return cog.bot.user_cache[user_id]

    # Otherwise, let's create it
    except KeyError:

        # Get the user's skills
        user_skill_rows = await db(
            "SELECT * FROM user_skill WHERE user_id = $1", user_id
        )
        user_skills = [Skill(**i) for i in user_skill_rows]

        # Now let's get the user's pp
        try:
            pp_rows = await db("SELECT * FROM user_pp WHERE user_id = $1", user_id)
            user_pp = Pp(**pp_rows[0])

        # apparently the user doesn't have pp? Let's create one
        except IndexError:
            user_pp = Pp(user_id)

        # Now we add this to the user cache
        cog.bot.user_cache[user_id] = CachedUser(user_id, user_skills, user_pp)

        # we do a little logging. it's called: "We do a little logging"
        cog.logger.info(f"Creating user cache for {user_id}... success")

        # and return the user cache
        return cog.bot.user_cache[user_id]
