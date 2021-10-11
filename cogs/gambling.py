# pylint: disable=unused-variable
# pylint: enable=too-many-lines

import discord
from discord.ext import commands
import random
import json
import userdata as ud


class gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["bet"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @ud.has_pp()
    async def gamble(self, ctx, amount):
        embed = await ud.create_embed(ctx)
        pp = await ud.Pp.fetch(ctx.author.id, self.bot)

        amount = pp.size if amount == "all" else int(amount)
        if pp.size < amount:
            embed.description = f"{ctx.author.mention}, your pp isnt big enough! You need **{amount} inches** to gamble this amount!"
            return await ctx.send(embed=embed)
        maxamount = 10 ** 5 if pp.multiplier["voted"] else 10 ** 3
        if amount > maxamount or amount < 2:
            embed.description = f"{ctx.author.mention}, you cant gamble that ammount! At most you can gamble **{maxamount // 10 ** 3}k inches. [VOTERS CAN GAMBLE UP TO 100K!](https://top.gg/bot/735147633076863027)**"
            return await ctx.send(embed=embed)

        botroll = random.randint(1, 12)
        humanroll = random.randint(1, 12)

        if botroll == humanroll:
            outcome = "draw!"
        elif botroll > humanroll:
            outcome = f"You lose **{amount} inches.**"
            pp.size -= amount
        else:
            outcome = f"You win **{amount} inches!**"
            pp.size += amount

        embed.title = f"{ctx.author.display_name} decides to gamble {amount} inches"
        embed.description = f"{outcome}\n\nYou now have {pp.size} inches."
        embed.add_field(
            name=f"{ctx.author.display_name}", value=f"Landed on `{humanroll}`"
        )
        embed.add_field(name=f"pp bot", value=f"Landed on `{botroll}`")
        await pp.update()
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(gambling(bot))
