import discord
from discord.ext import commands
import userdata as ud

import asyncio


class important(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


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
        pp = ud.Pp(user.id)
        if choice == 'size':
            await pp.size_add(int(arg1))
        elif choice == 'multiplier':
            await pp.multiplier_add(int(arg1))
        elif choice == 'name':
            await pp.rename(str(arg1))
        else:
            await ctx.message.add_reaction('❌')
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
            item = ud.Shop.Item(item_name)
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
            await item.add(item_type,item_desc,default_price,multiplierDependant)
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




def setup(bot):
    bot.add_cog(important(bot))