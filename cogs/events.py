import discord
from discord.ext import commands
import random, asyncio, re
import userdata as ud

class Events(commands.Cog):
    def __init__(self, bot:commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx):
        await ud.runsql('execute','UPDATE userdata.stats SET commands_run = userdata.stats.commands_run + 1')
        if random.randint(1,200)!=1: # 0.5% chance
            return
        #event is triggered
        await asyncio.sleep(1)
        string = random.choice([
            'pp bot time',
            'tax evasion',
            'frog',
            'peepee poopoo',
            'gambling addiction',
            'cool kids',
            'human rights',
            ])
        event = ud.Event(ctx.channel.id,string[::-1])
        await event.create()
        embed = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])),title='**EVENT**')
        embed.description = 'A random event has been triggered!'
        embed.add_field(name='Reverse!',value=f'Type **`{string}`** backwards')
        eventmsg = await ctx.send(embed=embed)
        await asyncio.sleep(30)
        embed = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])))
        if not await event.first():
            embed.title = 'nobody won lmaoooo'
        else:
            size = random.randint(50,200)
            first = await ud.Pp.fetch(await event.first(), get_multiplier=False)
            first.size += size * 3
            await first.update()
            
            embed.add_field(name='🥇 first place', value=f'{first.name} wins {size * 3} inches!',inline=False)
            if await event.second():
                second = await ud.Pp.fetch(await event.second(), get_multiplier=False)
                second.size += size * 2
                await second.update()
                embed.add_field(name='🥈 second place', value=f'{second.name} wins {size * 2} inches!',inline=False)
                
            if await event.third():
                third = await ud.Pp.fetch(await event.third(), get_multiplier=False)
                third.size += size
                await third.update()
                embed.add_field(name='🥉 third place', value=f'{third.name} wins {size} inches!',inline=False)
        
        await ctx.send(embed=embed)
        await eventmsg.delete()
        return await event.delete()
    
    @commands.Cog.listener()
    @commands.has_permissions(send_messages=True)
    async def on_message(self, message, embed_links=True):
        if message.author.bot:
            return
        #if message.content == 'reee':
        # return await message.channel.send(f'**REEE{"E"*random.randint(1,40)}** <a:reee:812625046543663114>')
        event = ud.Event(message.channel.id,message.content.lower())
        if await event.check():
            pp = await ud.Pp.fetch(message.author.id)
            #no pp
            if not pp:
                embed = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])))
                embed.description = f"{message.author.mention}, you need a pp first! Get one using `pp new`!"
                return await message.channel.send(embed=embed)
            #yes pp
            unplayable = await event.unplayable(pp.user_id)
            if unplayable:
                if unplayable == 1:
                    await message.channel.send(f'{message.author.mention} dude you cant enter the compition twice lmao')
                if unplayable == 2:
                    await message.channel.send(f'{message.author.mention} should\'ve been faster')
                return
            place = await event.setplace(pp.user_id)
            return await message.channel.send(f'{message.author.mention} got {place.replace("_"," ")}!')

def setup(bot):
    bot.add_cog(Events(bot))