import discord
import userdata as ud
import typing
import asyncio
import os
import io
import textwrap
import asyncpg
import json
import aiohttp
from discord.ext import commands
from datetime import datetime
import contextlib
import traceback
import toml


class Nerd(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        with open("./config.toml") as f:
            self.config = toml.loads(f.read())

    @commands.command()
    @commands.is_owner()
    async def iamyourcommander(self,ctx):
        async with ctx.typing():
            await asyncio.sleep(.1)
        return await ctx.send('Yes. You are')
            
    @commands.group(name="db",invoke_without_command=True)
    @commands.is_owner()
    async def db(self, ctx):
        async with ctx.typing():
            await asyncio.sleep(.1)
        return await ctx.send('```asciidoc\n= Database Help =\nA list of commands\n=====\n- give <user> <choice> <arg>```')
    
    @db.command(name="give")
    @commands.is_owner()
    async def db_update(self, ctx, user:discord.User, choice:str, *, arg1):
        async with ctx.typing():
            await asyncio.sleep(.1)
        pp = await ud.Pp.fetch(user.id)
        if choice == 'size':
            pp.size += int(arg1)
        elif choice == 'multiplier':
            pp.default_multiplier += int(arg1)
        elif choice == 'name':
            pp.name = str(arg1)
        else:
            return await ctx.message.add_reaction('❌')
        await pp.update()
        return await ctx.message.add_reaction('👌')

    @db.group(name="shop",invoke_without_command=True)
    @commands.is_owner()
    async def shop(self,ctx):
        async with ctx.typing():
            await asyncio.sleep(.1)
        return await ctx.send('```asciidoc\n= Shop Database Help =\nA list of commands\n=====\n- add <item_name>\n- set <item_name> <property> <arg>```')
    
    @shop.command(name="add")
    @commands.is_owner()
    async def db_shop_add(self, ctx, *, item_name:str):
        async with ctx.typing():
            def check(m):
                return m.author == ctx.author
            item = item.lower()
            await asyncio.sleep(.1)
        await ctx.send('What\'s the item type?')
        try:
            x = await self.bot.wait_for('message', timeout=120.0, check=check)
            item_type = str(x.content.upper())
            await ctx.send('What\'s the item description?')
            x = await self.bot.wait_for('message', timeout=120.0, check=check)
            item_desc = str(x.content)
            await ctx.send('What\'s the default price?')
            x = await self.bot.wait_for('message', timeout=120.0, check=check)
            default_price = int(x.content)
            await ctx.send('Is the item multiplier dependant?')
            x = await self.bot.wait_for('message', timeout=120.0, check=check)
            multiplierDependant = x == 'yes'
            await ud.Shop.add_item(item_name,item_type,item_desc,default_price,multiplierDependant)
            await ctx.send('Process completed.')
        except asyncio.TimeoutError:
            await ctx.send('Slowpoke.')

    @shop.command(name="set")
    @commands.is_owner()
    async def db_shop_set(self, ctx, column,arg,*,item_name):
        async with ctx.typing():
            await asyncio.sleep(.1)
        await ud.runsql('execute',f"UPDATE userdata.shopItems set {column} = {arg} WHERE item_name = '{item_name}'")
    
    @shop.command(name="delete")
    @commands.is_owner()
    async def db_shop_delete(self, ctx, *, item_name:str):
        async with ctx.typing():
            await asyncio.sleep(.1)
        await ud.runsql('execute',f"DELETE FROM userdata.shopItems WHERE item_name = '{item_name}'")
    
    @commands.command()
    @commands.is_owner()
    async def runsql(self, ctx, *, sql:str):
        start_time = datetime.now()
        async with ud.DatabaseConnection() as db:
            fetched = await db(sql)

        fetched = json.dumps(ud.deepdict(fetched), indent='  ')
        time_passed = datetime.now() - start_time
        if len(fetched) + 15 > 1500:
            txtfile = io.StringIO()
            txtfile.write(fetched)
            txtfile.seek(0)
            return await ctx.send(f"Executed in **{round(time_passed.total_seconds(), 3)}** seconds.", file=discord.File(txtfile, "fetched.json"))
        return await ctx.send(f"Executed in **{round(time_passed.total_seconds(), 3)}** seconds.\n```json\n{fetched}```")

    @commands.command()
    async def messageinfo(self, ctx, message:typing.Optional[discord.Message]):
        if not ctx.message.is_system:
            return
        
        headers = {
                "Authorization": f"Bot {self.config['admin']['TOKEN']}"
            }
        start_time = datetime.now()

        async with aiohttp.ClientSession() as session:
            if ctx.message.reference is None:
                payload = await session.get(f"https://discord.com/api/channels/{ctx.channel.id}/messages/{message.id}", headers=headers)
            else:
                payload = await session.get(f"https://discord.com/api/channels/{ctx.channel.id}/messages/{ctx.message.reference.message_id}", headers=headers)
        
        payload = json.dumps(await payload.json(), indent='  ')
        time_passed = datetime.now() - start_time
        if len(payload) + 15 > 1500:
            txtfile = io.StringIO()
            txtfile.write(payload)
            txtfile.seek(0)
            return await ctx.send(f"Executed in **{round(time_passed.total_seconds(), 3)}** seconds.", file=discord.File(txtfile, "payload.json"))
        return await ctx.send(f"Executed in **{round(time_passed.total_seconds(), 3)}** seconds.\n```json\n{payload}```")
    
    @commands.command(aliases=["exec", "execute", "ev"])
    @commands.is_owner()
    async def eval(self, ctx, *, code:str):
        async with ctx.typing():
            start_time = datetime.now()
            code = ud.clean_code(code)
            local_variables = {
                "discord": discord,
                "commands": commands,
                "bot": self.bot,
                "channel": ctx.channel,
                "guild": ctx.guild,
                "author": ctx.author,
                "ctx": ctx,
                "ud": ud,
            }

            stdout = io.StringIO()

            try:
                with contextlib.redirect_stdout(stdout):
                    exec(
                        f"async def func():\n{textwrap.indent(code, '    ')}", local_variables
                    )

                    obj = await local_variables["func"]()
                    result = f"{stdout.getvalue()}\n-- {obj}"
            except Exception as e:
                result = f"{traceback.format_exc()}\n\n{e}"

            time_passed = datetime.now() - start_time
            if len(result) > 1500:
                txtfile = io.StringIO()
                txtfile.write(result)
                txtfile.seek(0)
                return await ctx.send(
                    f"Executed in **{round(time_passed.total_seconds(), 3)}** seconds.",
                    file=discord.File(txtfile, "result.py")
                    )

            await ctx.send(
                f"Executed in **{round(time_passed.total_seconds(), 3)}** seconds.",
                embed=discord.Embed(description=f'```py\n{result}```')
                )

def setup(bot):
    bot.add_cog(Nerd(bot))