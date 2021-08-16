import logging

import toml
import voxelbotutils as vbu

from cogs import utils


class EconomyCommands(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        
        data = toml.load("config/items.toml")
        try:
            self.bot.items.clear()
            self.bot.logger.info("Clearing items cache... success")
        except AttributeError:
            self.bot.logger.warn("Clearing items cache... failed - No items cached")
        self.bot.items = {
            "shop": {
                i["id"]: utils.Item.from_dict(i) for i in data["items"] if i["shop_settings"]["buyable"]
            },
            "auction": {
                i["id"]: utils.Item.from_dict(i) for i in data["items"] if i["shop_settings"]["auctionable"]
            },
            "all": {
                i["id"]: utils.Item.from_dict(i) for i in data["items"]
            },
        }
        self.bot.logger.info("Caching items... success")


def setup(bot: vbu.Bot):
    x = EconomyCommands(bot)
    bot.add_cog(x)
