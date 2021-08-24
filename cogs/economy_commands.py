import logging
import os
import sys
import typing

import toml

import voxelbotutils as vbu
import discord
from discord.ext import commands, tasks


from cogs import utils


class EconomyCommands(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)

        # Let's clean up the items cache
        try:
            self.bot.items.clear()
            self.logger.info("   * Clearing items cache... success")

        # No cache to clean? then we don't need to do anything
        except AttributeError:
            self.logger.warn(
                "   * Clearing items cache... failed - No items cached")

        # Now let's load the items
        # Load each location from ./config/locations
        directory = r"config\items"
        items = []
        for filename in os.listdir(directory):
            if filename.endswith(".toml"):
                items.append(
                    utils.Item.from_dict(
                        toml.load(os.path.join(directory, filename))
                    )
                )

        self.bot.items = {
            "shop": {i.id: i for i in items if i.shop_settings.buyable},
            "auction": {i.id: i for i in items if i.shop_settings.auctionable},
            "all": {i.id: i for i in items},
        }
        self.logger.info("   * Caching items... success")

        # No user cache? Let's create it
        if not hasattr(self.bot, "user_cache"):
            self.bot.user_cache = {}
            self.logger.info("   * Creating user cache... success")

        # Now let's start the update db from user cache task
        self.update_db_from_user_cache.start()
        self.logger.info(
            "   * Starting update db from user cache task... success")

        # Now we clean up the begging cache
        try:
            self.bot.begging.clear()
            self.logger.info("   * Clearing begging cache... success")

        # No cache to clean? then we don't need to do anything
        except AttributeError:
            self.logger.warn(
                "   * Clearing begging cache... failed - No begging information cached")

        # Load each location from ./config/locations
        directory = r"config\begging\locations"
        begging_locations = []
        for filename in os.listdir(directory):
            if filename.endswith('.toml'):
                begging_locations.append(
                    utils.begging.BeggingLocation.from_dict(
                        toml.load(os.path.join(directory, filename))
                    )
                )

        # Put the locations into the bot's begging cache
        self.bot.begging = {
            "locations": utils.begging.BeggingLocations(begging_locations),
        }

    def cog_unload(self):
        self.update_db_from_user_cache.cancel()

    async def get_user_cache(self, user_id: int, db: typing.Optional[vbu.DatabaseConnection]) -> typing.Dict[utils.Skill, utils.Pp]:
        """
        Returns user's cached information, if any. Otherwise returns data from the database.

        Args:
            user_id (`int`): The user's ID.
            db (:class:`voxelbotutils.DatabaseConnection`): The database connection.

        Returns:
            `dict`: The user's cache.
        """

        # If the user is already cached, return it
        try:
            return self.bot.user_cache[user_id]

        # Otherwise, let's create it
        except KeyError:
            # Get the user's skills
            user_skills = [
                utils.Skill(**i) for i in await db("SELECT * FROM user_skill WHERE user_id = $1", user_id)
            ]

            # Now let's get the user's pp
            try:
                user_pp = utils.Pp(
                    **(await db("SELECT * FROM user_pp WHERE user_id = $1", user_id))[0]
                )

            # apparently the user doesn't have pp? Let's create one
            except IndexError:
                user_pp = utils.Pp(user_id)

            # Now we add this to the user cache
            self.bot.user_cache[user_id] = {
                "skills": user_skills,
                "pp": user_pp,
            }

            # we do a little logging. it's called: "We do a little logging"
            self.logger.info(
                f"Creating user cache for {user_id}... success")

            # and return the user cache
            return self.bot.user_cache[user_id]

    @tasks.loop(seconds=30.0)
    async def update_db_from_user_cache(self) -> None:
        """
        This task updates the database from the user cache every minute.
        """

        self.logger.info("Updating database from user cache...")

        # Establish a connection to the database
        async with vbu.DatabaseConnection() as db:

            # Iterate through all cached users
            for user_id, values in self.bot.user_cache.items():

                # Now we unpack the cached values
                skills, pp = values.values()

                # Iterate through all of their skills
                skill: utils.Skill
                for skill in skills:

                    # Update the user's skill
                    await db("""
                        INSERT INTO user_skill VALUES ($1, $2, $3)
                        ON CONFLICT (user_id, name) DO UPDATE SET user_skill = user_skill.experience + $3
                        """, user_id, skill.name, skill.experience
                    )

                    # Log our update
                    self.logger.info(
                        f"Updating user cache for {user_id} - {skill.name!r}... success")

                # Update the user's pp
                await db("""
                    INSERT INTO user_pp VALUES ($1, $2, $3, $4) ON CONFLICT (user_id) DO UPDATE
                    SET user_id = $1, name = $2, size = $3, multiplier = $4
                    """, user_id, pp.name, pp.size, pp.multiplier
                )

                # Log our update
                self.logger.info(
                    f"Updating user cache for {user_id}'s pp: {pp.name!r}... success")

    # Skills
    @commands.command(name='beg')
    async def _beg_command(self, ctx: commands.Context):
        """
        Level up begging, earn items, and get a large pp in the process!
        """

        await ctx.send(self.bot.begging["locations"])


def setup(bot: vbu.Bot):
    x = EconomyCommands(bot)
    bot.add_cog(x)
