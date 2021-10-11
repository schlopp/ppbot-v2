import discord
from discord.ext import commands
import random


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def destroy(self, ctx, user: discord.Member):
        random_object = random.choice(
            [
                "Two Trucks",
                "Schlopp's Face",
                "The Impostor",
                "Knowledge",
                "A 19 Dollar Fortnite Card",
                "Big Hot Men",
                "Coffee",
                "Ghigeon",
                "Knives",
                "Some Orphans",
            ]
        )
        return await ctx.send(
            f"destroys **{user.display_name}** with **{random_object}**"
        )


def setup(bot):
    bot.add_cog(Misc(bot))
