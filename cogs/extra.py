# pylint: disable=unused-variable
# pylint: enable=too-many-lines

import discord
from discord.ext import commands
import json, random, asyncio
import userdata as ud
from customjson import load, update



class extra(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    @commands.command(aliases=['hospital'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def surgery(self, ctx):
        embed = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])))
        pp = ud.Pp(ctx.author.id)
        #no pp
        if not await pp.check():
                embed.description = f"{ctx.author.mention}, you need a pp first! Get one using `pp new`!"
                return await ctx.send(embed=embed)
        #yes pp
        if await pp.pp_size() < 25*await pp.multiplier():
            embed.description = f"{ctx.author.mention}, your pp isnt big enough! You need at least **{25*await pp.multiplier()} inches** to get surgery!"
            return await ctx.send(embed=embed)
        growsize = random.randrange(5, 14)*await pp.multiplier()
        embed.title = "HOSPITAL"
        embed.description = f"{ctx.author.mention} goes to the hospital for some pp surgery..."
        if random.randrange(1, 100)>=20:
            await pp.size_add(growsize)
            status = "SUCCESSFUL"
            message = f"The operation was successful! Your pp gained {growsize} inches! It is now {await pp.pp_size()} inches."
        else:
            await pp.size_add(-growsize)
            status = "FAILED"
            message = f"The operation failed. Your pp snapped and you lost **{growsize} inches.** 😭 It is now {await pp.pp_size()} inches."
        embed.add_field(name=status, value=message)
        return await ctx.send(embed=embed)
    
    
    @commands.command(aliases=['pray'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def beg(self, ctx):
        embed = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])))
        pp = ud.Pp(ctx.author.id)
        #no pp
        if not await pp.check():
                embed.description = f"{ctx.author.mention}, you need a pp first! Get one using `pp new`!"
                return await ctx.send(embed=embed)
        #yes pp
        name = random.choice([
            'obama',
            'roblox noob',
            'dick roberts',
            'johnny from johnny johnny yes papa',
            'shrek',
            'caleb',
            'bob',
            'walter',
            'napoleon bonaparte',
            'bob ross',
            'coco',
            'thanos',
            'don vito',
            'bill cosby',
            'ur step-sis',
            'pp god',
            'random guy',
            'genie',
            'the guy u accidentally made eye contact with at the urinal',
            'joe mom',
            'ur daughter',
            'Big Man Tyrone'
        ])
        
        if random.randrange(0, 5)!=1:
            donation_amount = random.randrange(1, 10)*await pp.multiplier()
            await pp.size_add(donation_amount)
            embed.description = f'**{name}** donated {donation_amount} inches to {ctx.author.mention}'
        else:
            quote = random.choice([
                'ew poor',
                'don\'t touch my pp',
                'my wife has a bigger pp than you',
                'broke ass bitch',
                'cringe poor',
                'beg harder',
                'poor people make me scared',
                'dont touch me poor person',
                'get a job',
                'im offended',
                'no u',
                'i dont speak poor',
                'you should take a shower',
                'i love my wife... i love my wife... i love my wife..',
                'drink some water',
                'begone beggar',
                'No.',
                'no wtf?'
            ])
            if name == 'thanos':
                quote = random.choice(['begone before i snap you', 'i\'ll snap ur pp out of existence'])
            elif name == 'bill cosby' or name == 'don vito':
                quote = random.choice(['dude im a registered sex offender what do you want from me', 'im too busy touching people'])
            elif name == 'ur step-sis':
                quote = 'i cant give any inches right now, im stuck'
            elif name == 'pp god':
                quote = 'begone mortal'
            elif name == 'genie':
                quote = 'rub me harder next time 😩'
            elif name == 'the guy u accidentally made eye contact with at the urinal':
                quote = 'eyes on your own pp man'
            elif name == 'joe mom':
                quote = random.choice(['you want WHAT?', 'im saving my pp for your dad'])
            elif name == 'Big Man Tyrone':
                quote = 'Every 60 seconds in Africa a minute passes.'
            embed.description = f'**{name}:** {quote}'
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(extra(bot))