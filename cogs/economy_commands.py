import logging
import typing

import toml
import voxelbotutils as vbu

from cogs import utils


class EconomyCommands(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        
        data = toml.load("config/items.toml")

        # Let's clean some stuff up
        try:
            self.bot.items.clear()
            self.bot.logger.info("Clearing items cache... success")
        
        # No cache to clean? then we don't need to do anything
        except AttributeError:
            self.bot.logger.warn("Clearing items cache... failed - No items cached")
        
        # Now let's load the items
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
    
    async def get_user_cache(self, user_id: int, db: typing.Optional[vbu.DatabaseConnection] = None) -> typing.Dict[utils.Skill, utils.Pp]:

        # If the user is already cached, return it
        try:
            return self.bot.user_cache[user_id]
        
        # Otherwise, let's create it
        except KeyError:
            async with vbu.DatabaseConnection() as db:

                # Get the user's skills
                user_skills = [
                    utils.Skill(**i) for i in await db.fetch("SELECT * FROM user_skills WHERE user_id = $1", user_id)
                ]

                # Now let's get the user's pp
                try:
                    user_pp = utils.Pp(
                        **await db.fetch("SELECT * FROM user_pp WHERE user_id = $1", user_id)[0]
                    )
                
                # apparently the user doesn't have pp? Let's create one
                except IndexError:
                    user_pp = utils.Pp()
                
                # Now we add this to the user cache
                self.bot.user_cache[user_id] = {
                    "skills": user_skills,
                    "pp": user_pp,
                }
            
            # we do a little logging. it's called: "We do a little logging"
            self.bot.logger.info(f"Creating user cache for {user_id}... success")


def setup(bot: vbu.Bot):
    x = EconomyCommands(bot)
    bot.add_cog(x)
