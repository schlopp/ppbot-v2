import typing
import discord
import voxelbotutils as vbu
from cogs import utils
from discord.ext import commands


class Shop(vbu.Cog):

    @vbu.command(name='shop', aliases=['store', 'itemshop'])
    async def _shop_command(self, ctx:vbu.Context):
        """
        Shoppy woppy
        """
        pass


def setup(bot:vbu.Bot):
    x = Shop(bot)
    bot.add_cog(x)