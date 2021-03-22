import asyncpg
import discord
import toml
import random
from userdata import Pp, Inv
from discord.ext import commands

with open("./config.toml") as f:
    config = toml.loads(f.read())

class SQLMethodError(Exception):
    """SQL Method Error"""
    
    def __init__(self, method):
        self.method = method
        super().__init__('SQL Method unkown')
    
    def __str__(self):
        return f'SQL Method: "{self.method}" unknown\033[0m'


async def fetch(pgselect:str,pgfrom:str,pgwhere:str=None):
    """returns the return value of a fetched premade-sql statement\n\n__\n\nsql statement:\n\n- `SELECT {pgselect} FROM {pgfrom}( WHERE {pgwhere}; || ;  )`"""
    pgwhere = " WHERE {pgwhere};" if pgwhere else f";"
    conn = await asyncpg.connect(config['admin']['PSQL'])
    fetched = await conn.fetch(
        f'''
        SELECT {pgselect} FROM {pgfrom}{pgwhere}
        '''
        )
    await conn.close()
    return [dict(i) for i in fetched]


async def runsql(method:str,sqlstring:str):
    conn = await asyncpg.connect(config['admin']['PSQL'])
    if method == "execute":
        await conn.execute(sqlstring)
        return await conn.close()
    elif method == "fetch":
        fetched = await conn.fetch(sqlstring)
        await conn.close()
        return fetched
    else:
        await conn.close()
        raise SQLMethodError(method=method)

        
async def create_embed(ctx:commands.Context, **kwargs):
    """
    kwargs:
    user - `discord.Member` (default discord.ext.commands.Context)\n
    return_user - `bool` (default False)\n
    include_tip - `bool` (default True)\n
    pp_dependent - `bool` (default True)\n
    pp_adjective - `bool` (default False)\n
    item_required - `String | None` (default None)\n
    """
    embed:discord.Embed = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])))
    user = kwargs.get('user', ctx.author)
    return_user:bool = kwargs.get('return_user',False)
    include_tip:bool = kwargs.get('include_tip',True)
    pp_dependent:bool = kwargs.get('pp_dependent',True)
    pp_adjective:bool = kwargs.get('pp_adjective',False)
    item_required = kwargs.get('item_required',None)
    usercheck = user == ctx.author
    pp = Pp(user.id)
    check = await pp.check()
    
    
    exception = None
    if pp_dependent and not check:
            exception = f"{user.mention}, you need a pp first! Get one using `pp new`!" if usercheck else "that person doesnt have a cock. (might be a trap)"
    if pp_adjective and check:
            exception = f"{user.mention}, you already have a pp :("
    if item_required:
        inv = Inv(user.id)
        if not await inv.has_item(item_required):
            exception = f'you need a "{item_required}" to use this command. Check if its for sale at the shop!'
    if include_tip and random.randint(1,10)==1:
        embed.add_field(name="TIP:",value=random.choice([
            "Tools in the shop unlock commands!",
            "There's a small chance of an event happening upon using a command!",
            "You can see the leaderboard by using the `pp leaderboard` command!",
            "There are a ton of fun commands! Have you tried them yet?",
            "[Invite my friend's pigeon pet bot!](https://top.gg/bot/753013667460546560)",
            "Join the official pp bot server! use `pp support`",
            "Add pp bot to your server! use `pp invite`"
        ]))
    if return_user:
        return embed,pp,user,exception
    return embed,pp,exception


async def handle_exception(ctx:commands.Context, exception:str):
    embed = discord.Embed(colour=discord.Colour(0xff0000))
    embed.title = f"Oopsie {ctx.author.display_name}, something went wrong."
    embed.description = exception
    return await ctx.send(embed=embed)
