import discord
from discord.ext import commands
import asyncio
import random
import io
import json
import aiohttp



class helping(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        #Help command
    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def help(self, ctx, *, category=None):
        advert = random.choice([
            'click me!',
            'invite me!',
            'click here!',
            'click on me!'
        ])
        embed                   = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])))
        
        embed.title             = "help | " + advert
        embed.url               = "https://discord.com/oauth2/authorize?client_id=735147633076863027&scope=bot&permissions=2147863616"
        embed.description       = "pp bot. Grow your own pp today!"
        embed.set_thumbnail(url = "https://cdn.discordapp.com/avatars/735147633076863027/a34d69e6d5e2021fc64caa69f642e37b.webp?size=1024")
        embed.set_footer(text   = "\""+random.choice(["big pp gang","my gf has a bigger pp than me","wtf is this bot","i love my wife"])+"\"")

        embed.add_field(
            name   = "**pp commands**",
            value  = """
`new, show @user, grow, rename`
            """,
        inline = True
        )
        embed.add_field(
            name   = "**Shop commands**",
            value  = """
`shop, buy <amount> <item>`
            """,
        inline = True
        )
        embed.add_field(
            name   = "**Gambling commands**",
            value  = """
`gamble <amount>`
            """,
        inline = True
        )
        embed.add_field(
            name   = "**Fun commands**",
            value  = """
`cat, dog, fox, redpanda, panda, meme, compare @user, percentage <thing>, snort`
            """,
        inline = True
        )
        embed.add_field(
            name   = "**Extra economy commands**",
            value  = """
`hospital, fish, hunt, beg, daily`
            """,
        inline = True
        )
        embed.add_field(
            name   = "**Utility commands**",
            value  = """
`sfwtoggle, leaderboard @user, suggest, github, vote`
            """,
        inline = True
        )
        embed.add_field(
            name   = "**Help commands**",
            value  = """
`help, invite, support`
            """,
        inline = True
        )
        return await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(helping(bot))
