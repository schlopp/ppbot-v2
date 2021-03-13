# pylint: disable=unused-variable
# pylint: enable=too-many-lines

import discord
from discord.ext import commands
import asyncio
import random
import io
import json
import aiohttp
import re
import userdata as ud
from decimal import Decimal



class testing(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    @commands.command(aliases=["hug", "kiss","kill"])
    async def slap(self, ctx, personBeingSlapped:discord.Member):
        slapmessage = random.choice([
            f"gives **{personBeingSlapped.display_name}** a dirty slap",
            f"slams **{personBeingSlapped.display_name}** into the ground",
            f"punches **{personBeingSlapped.display_name}** and calls them a bitch boy"
        ])
        slap = discord.Embed(colour=discord.Colour(11922135))
        slap.description = f"***{ctx.author.display_name}** {slapmessage}*"
        await ctx.send(embed=slap)
        
    @commands.command()
    async def cookie(self, ctx, who:discord.Member=None):
        await ctx.send(f"*gives cookie to {who.mention}*")
        
    @commands.command()
    @commands.is_owner()
    async def spam(self, ctx, person:discord.Member, times:int):
        if ctx.author.id != 393305855929483264:
            return
        for i in range(times):
            await ctx.send(person.mention)
    
    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
            await ctx.send(len(self.bot.guilds))
    
    @commands.command()
    async def avatar(self, ctx, member:discord.Member=None):
        await ctx.send(member.avatar_url if member != None else ctx.author.avatar_url)

    @commands.command()
    @commands.is_owner()
    async def embed(self, ctx, *, new_title):
        await ctx.send(embed=discord.Embed(title=new_title))
    
    @commands.command()
    @commands.is_owner()
    async def space(self, ctx, *, text):
        await ctx.send(f"```{''.join(text.split())}```")

    @commands.command(aliases=['blowjob', 'bj', 'fuck'])
    @commands.is_nsfw()
    async def suck(self, ctx, who:discord.Member):
        await ctx.send(f"*sucks {who.mention} dick and calls them {random.choice(['papi', 'daddy','big dick ronny'])}*")

    @commands.command(aliases=['purge'])
    @commands.has_guild_permissions(manage_messages=True)
    async def clear(self, ctx, ammount, *, optional=None):

        if ammount == 'help':
            await ctx.send('```.clear <ammount> <*optional* user | regex *optional*>\n\naliases: "purge", "delete"\ndescription: delete messages in bulk.```')
        elif optional == None:
            await ctx.channel.purge(limit=int(ammount))
        elif re.search("^r.", optional):
            await ctx.send(optional[2:])
            def clear_check(message):
                #print(f'--- searching for {optional[2:]} inside {message.content}')
                #print(f'result: {re.search(optional[2:], message.content)}\n---')
                if re.search(optional[2:], message.content):
                    return message
            await ctx.channel.purge(limit=int(ammount)+1,check=clear_check)
        else:
            member = await commands.MemberConverter().convert(ctx, optional)
            def clear_check(message):
                return message.author.id == member.id
            await ctx.channel.purge(limit=int(ammount)+1,check=clear_check)


    @commands.command()
    @commands.is_owner()
    async def infcat(self, ctx):
        for i in range(1000):
            async with aiohttp.ClientSession() as session:
                async with session.get('http://aws.random.cat/meow') as r:
                    if r.status == 200:
                        js = await r.json()
                        e = discord.Embed(title=random.choice(['very cute', '10/10', 'meow']))
                        e.set_image(url=js['file'])
                        themessage = await ctx.send(embed=e)
                        await themessage.add_reaction('❤️')
                        await asyncio.sleep(50)


    @commands.command()
    @commands.is_owner()
    async def role(self, ctx, action:str="give", firstarg=None, secondarg=None):
        if action == "create":
            role = await ctx.guild.create_role(name=str(firstarg) if firstarg != None else 'Untitled Role')
            await ctx.send(f"**{ctx.author}** Created the role **\"{role.name}\"** with the id **\"{role.id}\"**")
        elif action in ['give', 'add']:
            if firstarg != None:
                try:
                    member = await commands.MemberConverter().convert(ctx, firstarg)
                except:
                    member = ctx.author
                try:
                    role = ctx.guild.get_role(int(secondarg)) if secondarg != None else ctx.guild.get_role(int(firstarg))
                except:
                    role = None
                await member.add_roles(role)
                try:
                    await ctx.send(f"**{ctx.author}** gave the role **\"{role.name}\"** with the id **\"{role.id}\"** to **{member}**")
                except:
                    await ctx.send("Role with the ID **%s** not found" % secondarg if secondarg != None else firstarg)
        elif action == "edit":
            if firstarg != None:
                try:
                    author, channel = ctx.author, ctx.channel
                    role = ctx.guild.get_role(int(firstarg))
                    await ctx.send(f"What do you want to edit about the role **\"{role.name}\"** with the id **\"{role.id}\"**?")
                    def check(m):
                        return m.author == author and m.channel == channel
                    try:
                        permission = await self.bot.wait_for("message", timeout=30.0, check=check)
                        if permission.content.lower() == "name":
                            await ctx.send(f"Enter a new name:")
                            new_name = await self.bot.wait_for("message", timeout=30.0, check=check)
                            old_name = role.name
                            await role.edit(name=new_name.content)
                            await ctx.send(f"**{ctx.author}** Updated the role **\"{old_name}\"** with the id **\"{role.id}\"**\nNew name: **\"{role.name}\"**")
                        elif permission.content.lower() == "permissions":
                            await ctx.send(f"""
```
Permission types
                            
1. Default -- All Default settings.
2. Mod -- All Default settings plus moderation settings such as managing messages, managing usernames, banning, kicking.
3. Admin -- All settings.
```
Which permission type do you want to change the role **\"{role.name}\"** with the id **\"{role.id}\"** to?
                            """)
                            permission_type = await self.bot.wait_for("message", timeout=30.0, check=check)
                            await ctx.send(role.permissions)
                            if permission_type.content == "1":
                                await role.edit(permissions=discord.Permissions(permissions=3509312))
                            elif permission_type.content == "2":
                                await role.edit(permissions=discord.Permissions(permissions=234220758))
                            elif permission_type.content == "3":
                                await role.edit(permissions=discord.Permissions(permissions=2113400062))
                            await ctx.send(f"**{ctx.author}** Updated the role **\"{role.name}\"** with the id **\"{role.id}\"**\nNew permission type: **\"{permission_type.content}\"**")
                    except asyncio.TimeoutError:
                        await ctx.send('Times up to respond.')
                except:
                    await ctx.send(f"404, Invalid ID or Missing")


        if re.search("\?$",ctx.message.content):
            responce = random.choice([
                "Yes.",
                "No.",
                "Ofcourse.",
                "Are you stupid?",
                "What? Ofcourse not",
                "I think you know the answer to that.",
                "Are you crazy?",
            ])
            await ctx.send(responce)
        await ctx.send("You need to ask a question using a question mark (?).")

    @commands.command()
    @commands.is_owner()
    async def egrs(self, ctx):
        await ctx.send(files=[discord.File("./ppstorage.json"),discord.File("./levels.json")])

    @commands.command()
    @commands.is_owner()
    async def runsql(self, ctx, method:str, *, sqlstring:str):
        if method == "execute":
            await ud.runsql(method,sqlstring)
            return await ctx.send('Done.')
        if method == "fetch":
            fetched = await ud.runsql(method,sqlstring)
            txtfile = io.StringIO()
            txtfile.write(str(fetched))
            txtfile.seek(0)
            return await ctx.send(file=discord.File(txtfile, "fetched.txt"))
        
    @commands.command()
    @commands.is_owner()
    async def testSTS(self, ctx, minimum:int=0):
        for i in self.bot.guilds:
            if i.member_count>=minimum:
                await ctx.send(f'server name:{i.name}\nmembers:{i.member_count}')
    
    @commands.command()
    @commands.is_owner()
    async def bruu(self, ctx, id:int):
        return await ctx.send(discord.utils.get(self.bot.get_all_members(),id=id))
    
    @commands.command()
    async def nablijven(self, ctx, member:discord.Member,*,time:str="het 9e uur"):
        await ctx.send(f'**{member.display_name}** moet nablijven tot {time}')
        
    @commands.command()
    async def bubblewrap(self, ctx):
        await ctx.send('||pop||'*200)
        
    @commands.command()
    @commands.is_owner()
    async def owner_check(self,ctx):
        return await ctx.send('haha yes you are my dad')
        
    @commands.command()
    @commands.is_owner()
    async def msd(self, ctx, channel:int, *, msg:str):
        channel = self.bot.get_channel(channel)
        await channel.send(msg)
        
    @commands.command()
    @commands.is_owner()
    async def cmdr(self, ctx):
        fetched = await ud.fetch('commands_run','userdata.stats')
        await ctx.send(f'Commands run: **{round(fetched[0]["commands_run"]/1000,1)}k.**')
    
    @commands.command()
    @commands.is_owner()
    async def vcjoin(self,ctx):
        await ctx.author.voice.channel.connect()
    @commands.command()
    @commands.is_owner()
    async def vcleave(self,ctx):
        await ctx.author.voice.channel.leave()

def setup(bot):
    bot.add_cog(testing(bot))