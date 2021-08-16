import toml

import voxelbotutils as vbu

from cogs import utils


class EconomyCommands(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        self.bot = bot
        
        data = toml.load("config/items.toml")
        try:
            self.bot.items.clear()
        except AttributeError:
            pass
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


def setup(bot: vbu.Bot):
    x = EconomyCommands(bot)
    bot.add_cog(x)
