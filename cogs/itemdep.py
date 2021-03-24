# pylint: disable=unused-variable
# pylint: enable=too-many-lines

import discord
from discord.ext import commands
import random
import json
import asyncio
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
        if random_number == 1000:#<= 45:
            options = {
                'shot a homeless man': random.randint(1,20)*await pp.multiplier(),
                'deadass just killed a man': random.randint(5,20)*await pp.multiplier(),
                'shot up a walmart': random.randint(10,30)*await pp.multiplier(),
                'hijacked a fucking orphanage and sold all the kids': random.randint(30,50)*await pp.multiplier()
                }
            choice = random.choice(list(options.items()))
            await pp.size_add(choice[1])
            embed.description = f"{ctx.author.mention} {choice[0]} for **{choice[1]} inches!**"
            return await ctx.send(embed=embed)
        else:
            options = {
                '[____] an ambulance! But not for me.': 'CALL',
                'You\'ll never [____] me alive! *doot*': 'TAKE',
                }
            choice = random.choice(list(options.items()))
            embed.description = f"{ctx.author.mention} tried to shoot a police officer but they shot back! **Fill in this sentence to dodge the bullets:**\n\n`{choice[0]}`"
            await ctx.send(embed=embed)
            try:
                await self.bot.wait_for('message',timeout=20.0,check=lambda m: m.content.upper() == choice[1] and m.author == ctx.author and m.channel == ctx.channel)
            except asyncio.TimeoutError:
                random_number = random.randint(1,50)
                currentsize = await pp.pp_size()
                if currentsize > 50:
                    await pp.size_add(-random_number)
                    embed.description = f"**Too slow!** The police officer shoots you and takes **{random_number} inches** from your corpse. The correct word was `{choice[1}`"
                else:
                    embed.description = "**Too slow!** The police officer shoots you and realises your pp is so small it's not even worth taking. The correct word was `{choice[1}`"
                return await ctx.send(embed=embed)
            if random_number < 30:
                options = [
                    'bronze coin',
                    'happy flour',
                    'fishing rod',
                    ]
                choice = random.choice(options)
                await inv.new_item(choice)
                embed.description = f"You avoid the bullet and loot the police officer. You find a **{choice}!**"
            else:
                await pp.size_add(random_number)
                embed.description = f"You avoid the bullet and loot the police officer. You find **{random_number} inches and 1 {choice}!**"
            await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(fishing(bot))
