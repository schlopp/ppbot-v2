import discord
from discord.ext import commands
import json, random, asyncio
import userdata as ud


class important(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 60*60*24, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @ud.has_pp()
    async def daily(self, ctx):
        async with ctx.typing():
            pp = await ud.Pp.fetch(ctx.author.id, self.bot)
            growsize = random.randrange(40, 80) * pp.multiplier["multiplier"]
            await pp.size_add(growsize)
            
            embed = await ud.create_embed(ctx)
            embed.description = f'{ctx.author.mention} received their daily **{growsize} inches!**'
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(important(bot))