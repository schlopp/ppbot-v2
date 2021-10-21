import typing
import logging
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
    settings: dict

    def __init__(
        self, user_id: int, skills: typing.List[Skill], pp: Pp, settings: dict
    ):
        """
        Represents a cached user.

        Args:
            user_id (int): The user's ID.
            skills (`list` of `:class:Pp`):  The user's cached skills.
            pp (`:class:Pp`):  The user's cached pp.
            settings (`dict`):  The user's cached settings. See `config/database.pgsql` for reference.
        """

        self.user_id = user_id
        self.skills = skills
        self.pp = pp
        self.settings = settings

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

    async def update_settings(self, key, value):

        # There is no safe, dynamic way to do this. :RIP:
        # View config/database.pgsql for reference.
        valid_columns = ["current_begging_location"]
        if key not in valid_columns:
            raise KeyError(
                f"{key} is not a valid column. View config/database.pgsql for reference."
            )

        # Don't open a costly database connection if we don't need to
        try:
            if self.settings[key] == value:
                return
        except KeyError:
            pass

        self.settings[key] = value
        async with vbu.DatabaseConnection() as db:
            await db(
                f"UPDATE user_settings SET {key} = $1 WHERE user_id = $2",
                value,
                self.user_id,
            )


async def get_user_cache(
    user_id: int,
    *,
    db: typing.Optional[vbu.DatabaseConnection],
    bot: vbu.Bot,
    logger: typing.Optional[logging.Logger] = logging.Logger(
        "CachedUser", level=logging.DEBUG
    ),
) -> CachedUser:
    """
    :coro: Returns user's cached information, if any. Otherwise returns data from the database.

    Args:
        bot (`:class:vbu.Bot`):  The bot.
        user_id (`int`): The user's ID.
        db (:class:`voxelbotutils.DatabaseConnection`): The database connection.
        logger (:class:`voxelbotutils.Logger` = :class:`Logger("utils.CacherUser")`): The logger.

    Returns:
        :class:`UserCache`: The user's cache.
    """

    # If the user is already cached, return it
    try:
        return bot.user_cache[user_id]

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

        # Get the user's settings
        try:
            settings_rows = await db(
                "SELECT * FROM user_settings WHERE user_id = $1", user_id
            )
            user_settings = dict(settings_rows)

        # No settings
        except IndexError:
            await db(
                "INSERT INTO user_settings (user_id) VALUES ($1)",
                user_id,
            )
            settings_rows = await db(
                "SELECT * FROM user_settings WHERE user_id = $1", user_id
            )
            user_settings = dict(settings_rows)

        # Now we add this to the user cache
        bot.user_cache[user_id] = CachedUser(
            user_id, user_skills, user_pp, user_settings
        )

        # we do a little logging. it's called: "We do a little logging"
        logger.debug(f"Creating user cache for {user_id}... success")

        # and return the user cache
        return bot.user_cache[user_id]
