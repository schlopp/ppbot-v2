import random
import typing

import voxelbotutils as vbu
import discord
from discord.ext import commands

from cogs import utils


class TestingCommands(vbu.Cog):

    @vbu.command(name='addgod')
    async def _add_god_command(self, ctx: vbu.Context):
        item = utils.Item(
            name='god himself lmao',
            type='TOTEM',
            shopsettings=utils.ShopSettings(True, buy=10_000, sell=2_000),
            rarity='LEGENDARY', auctionable=True, emoji=826952082371772423,
            lore=utils.Lore(
                'No use! Just for testing!',
                [
                    'how the fuck did god manage to get into this game? Oh well',
                    'Very sexy i must admit',
                ],
            ),
            requires=utils.Dict({'BEGGING': 10})
        )
        async with vbu.DatabaseConnection() as db:
            await db('''DELETE FROM items WHERE name = $1''', 'god himself lmao')
            await item.create(db)
    
    @vbu.command(name='name')
    async def _rename_pp_command(self, ctx: vbu.Context, *, name: str):
        async with vbu.DatabaseConnection() as db:
            async with utils.Pp.fetch(db, ctx.author.id) as pp:
                name = (name[:30] + '..') if len(name) > 32 else name
                pp.name = name
                return await ctx.reply(f'Renamed your pp to **{name}**!', mention_author=False)
    
    @vbu.command(name='grow')
    @vbu.cooldown.cooldown(1, 10)
    async def _grow_pp_command(self, ctx: vbu.Context):
        async with vbu.DatabaseConnection() as db:
            async with utils.Pp.fetch(db, ctx.author.id) as pp:
                growth = round(random.randint(1,100) * pp.multiplier)
                pp.size += growth
                return await ctx.reply(f'Your pp grew **{growth}** inches!', mention_author=False)
    
    @vbu.command(name='multiply')
    async def _multiply_pp_command(self, ctx: vbu.Context):
        async with vbu.DatabaseConnection() as db:
            async with utils.Pp.fetch(db, ctx.author.id) as pp:
                if round(50 * pp.multiplier) > pp.size:
                    return await ctx.reply(f'You need **{round(50 * pp.multiplier) - pp.size}** more inches!', mention_author=False)
                pp.multiplier = round(pp.multiplier + 0.05, 2)
                return await ctx.reply(f'Your multiplier is now **{pp.multiplier}x**!', mention_author=False)
    
    @vbu.command(name='randomnames')
    async def _random_names_command(self, ctx: vbu.Context, amount: typing.Optional[int] = 1):
        for _ in range(amount):
            await ctx.send(utils.random_name())


def setup(bot: vbu.Bot):
    x = TestingCommands(bot)
    bot.add_cog(x)
