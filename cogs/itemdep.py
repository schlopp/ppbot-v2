# pylint: disable=unused-variable
# pylint: enable=too-many-lines

import discord
from discord.ext import commands
import random
import json
from customjson import load, update
import userdata as ud



class fishing(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def fish(self, ctx):
        embed = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])))
        pp = ud.Pp(ctx.author.id)
        inv = ud.Inv(ctx.author.id)
        #no pp
        if not await pp.check():
                embed.description = f"{ctx.author.mention}, you need a pp first! Get one using `pp new`!"
                return await ctx.send(embed=embed)
        #yes pp
        #no fish
        if not await inv.has_item("fishing rod"):
            embed.description = f"lol {ctx.author.mention} you dont have a fishing rod. smh go buy one in the `pp shop`"
            return await ctx.send(embed=embed)
        random_number = random.randrange(1, 20)
        if random_number == 1:
            await inv.new_item("fishing rod", -1)
            embed.description = f"{ctx.author.mention} flung their fishing rod too hard and it broke lmaoo"
            return await ctx.send(embed=embed)
        if random_number == 2:
            embed.description = f"{ctx.author.mention} went fishing and caught nothing."
            return await ctx.send(embed=embed)
        fish_amount = random_number*await pp.multiplier()
        await pp.size_add(fish_amount)
        quote = random.choice(['Pretty cool huh?','Nice!','Epic!'])
        embed.description = f"{ctx.author.mention} went fishing and caught **{fish_amount} inches!** {quote}"
        return await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, 45, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def hunt(self, ctx):
        embed = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])))
        pp = ud.Pp(ctx.author.id)
        inv = ud.Inv(ctx.author.id)
        #no pp
        if not await pp.check():
                embed.description = f"{ctx.author.mention}, you need a pp first! Get one using `pp new`!"
                return await ctx.send(embed=embed)
        #yes pp
        #no rifle
        if not await inv.has_item("rifle"):
            embed.description = f"lol {ctx.author.mention} you dont have a rifle. smh go buy one in the `pp shop`"
            return await ctx.send(embed=embed)
        random_number = random.randrange(1, 50)
        if random_number == 1:
            await inv.new_item("rifle", -1)
            embed.description = f"{ctx.author.mention} got arrested and their rifle was confiscated."
            return await ctx.send(embed=embed)
        if random_number == 2:
            embed.description = f"{ctx.author.mention} shot a homeless man who had just gambled away the last of his inches."
            return await ctx.send(embed=embed)
        options = {'shot a homeless man': random.randint(1,20)*await pp.multiplier(),
                'deadass just killed a man': random.randint(5,20)*await pp.multiplier(),
                'shot up a walmart': random.randint(10,30)*await pp.multiplier(),
                'hijacked a fucking orphanage and sold all the kids': random.randint(30,50)*await pp.multiplier()}
        choice = random.choice(list(options.items()))
        await pp.size_add(choice[1])
        embed.description = f"{ctx.author.mention} {choice[0]} for **{choice[1]} inches!**"
        return await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(fishing(bot))