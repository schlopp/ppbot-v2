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
    @commands.command(aliases=['bet'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def gamble(self, ctx, amount):
        embed = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])))
        pp = ud.Pp(ctx.author.id)
        #no pp
        if not await pp.check():
                embed.description = f"{ctx.author.mention}, you need a pp first! Get one using `pp new`!"
                return await ctx.send(embed=embed)
        #yes pp
        amount = await pp.pp_size() if amount == "all" else int(amount)
        if await pp.pp_size() < amount:
            embed.description = f"{ctx.author.mention}, your pp isnt big enough! You need **{amount} inches** to gamble this amount!"
            return await ctx.send(embed=embed)
        if amount > 10000 or amount < 2:
            embed.description = f"{ctx.author.mention}, you cant gamble that ammount! **(minimum amount: 2, maximum amount: 10000)**"
            return await ctx.send(embed=embed)
        
        botroll = random.randint(1,12)
        humanroll = random.randint(1, 12)
        
        if botroll == humanroll:
            outcome = "draw!"
        elif botroll > humanroll:
            outcome = f"You lose {amount} inches."
            await pp.size_add(-amount)
        else:
            outcome = f"You win {amount} inches!"
            await pp.size_add(amount)
        embed.title = f"{ctx.author.display_name} decides to gamble {amount} inches"
        embed.description = f"{outcome}\n\nYou now have {await pp.pp_size()}."
        embed.add_field(name=f"{ctx.author.display_name}", value=f"Landed on `{humanroll}`")
        embed.add_field(name=f"pp bot", value=f"Landed on `{botroll}`")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(gambling(bot))