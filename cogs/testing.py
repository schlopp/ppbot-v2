import voxelbotutils as vbu
from cogs import utils
from discord.ext import commands


class TestingCommands(vbu.Cog):
    pass

def setup(bot:vbu.Bot):
    x = TestingCommands(bot)
    bot.add_cog(x)
