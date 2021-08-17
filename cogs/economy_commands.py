import logging
import typing

import toml

import voxelbotutils as vbu
import discord
from discord.ext import commands, tasks


from cogs import utils


class EconomyCommands(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        

        # Let's clean some stuff up
        try:
            self.bot.items.clear()
            self.bot.logger.info("Clearing items cache... success")
        
        # No cache to clean? then we don't need to do anything
        except AttributeError:
            self.bot.logger.warn("Clearing items cache... failed - No items cached")
        
        # Now let's load the items
        data = toml.load("config/items.toml")
        self.bot.items = {
            "shop": {
                # Buyable items
                i["id"]: utils.Item.from_dict(i) for i in data["items"] if i["shop_settings"]["buyable"]
            },
            "auction": {
                # Auctionable items
                i["id"]: utils.Item.from_dict(i) for i in data["items"] if i["shop_settings"]["auctionable"]
            },
            "all": {
                # All items
                i["id"]: utils.Item.from_dict(i) for i in data["items"]
            },
        }
        self.bot.logger.info("Caching items... success")
        
        # No user cache? Let's create it
        if not hasattr(self.bot, "user_cache"):
            self.bot.user_cache = {}
            self.bot.logger.info("Creating user cache... success")
        
        # Now let's start the update db from user cache task
        self.update_db_from_user_cache.start()
        self.bot.logger.info("Starting update db from user cache task... success")

        # Now we clean up the begging cache
        try:
            self.bot.begging.clear()
            self.bot.logger.info("Clearing begging cache... success")
        
        # No cache to clean? then we don't need to do anything
        except AttributeError:
            self.bot.logger.warn("Clearing begging cache... failed - No begging information cached")
        
        # Now we cache the begging information
        self.bot.begging = {
            "locations": utils.begging.BeggingLocations(
                *(utils.begging.BeggingLocation.from_dict(i) for i in toml.load('config/begging/locations.example.toml')['locations'])
            ),
        }
    
    def cog_unload(self):
        self.update_db_from_user_cache.stop()
    
    async def get_user_cache(self, user_id: int, db: typing.Optional[vbu.DatabaseConnection] = None) -> typing.Dict[utils.Skill, utils.Pp]:

        # If the user is already cached, return it
        try:
            return self.bot.user_cache[user_id]
        
        # Otherwise, let's create it
        except KeyError:
            async with vbu.DatabaseConnection() as db:

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
            self.bot.logger.info(f"Creating user cache for {user_id}... success")

            # and return the user cache
            return self.bot.user_cache[user_id]
    
    @tasks.loop(seconds=30.0)
    async def update_db_from_user_cache(self) -> None:
        """
        This task updates the database from the user cache every minute.
        """

        self.bot.logger.info("Updating database from user cache...")
    
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
                    self.bot.logger.info(f"Updating user cache for {user_id} - {skill.name!r}... success")

                # Update the user's pp
                await db("""
                    INSERT INTO user_pp VALUES ($1, $2, $3, $4) ON CONFLICT (user_id) DO UPDATE
                    SET user_id = $1, name = $2, size = $3, multiplier = $4
                    """, user_id, pp.name, pp.size, pp.multiplier
                )

                # Log our update
                self.bot.logger.info(f"Updating user cache for {user_id}'s pp: {pp.name!r}... success")


def setup(bot: vbu.Bot):
    x = EconomyCommands(bot)
    bot.add_cog(x)
