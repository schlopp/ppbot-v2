import asyncpg
import asyncio
import discord
import toml
import json
import aiohttp
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
    include_tip - `bool` (default True)\n
    """
    embed:discord.Embed = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])))
    include_tip:bool = kwargs.get('include_tip',True)
    if include_tip and random.randint(1,10)==1:
        embed.add_field(name="TIP:",value=random.choice([
            "Tools in the shop unlock commands!",
            "There's a small chance of an event happening upon using a command!",
            "You can see the leaderboard by using the `pp leaderboard` command!",
            "There are a ton of fun commands! Have you tried them yet?",
            "[Invite my friend's pigeon pet bot!](https://top.gg/bot/753013667460546560)",
            "Join the official pp bot server! use `pp support`",
            "Add pp bot to your server! use `pp invite`",
            "Did you know: MOOB has the all time record for the biggest pp!",
        ]))
    return embed


async def handle_exception(ctx:commands.Context, exception:str):
    embed = discord.Embed(colour=discord.Colour(0xff0000))
    embed.title = f"Oopsie {ctx.author.display_name}, something went wrong."
    embed.description = exception
    return await ctx.send(embed=embed)


async def get_user_topgg_vote(bot, user_id:int) -> bool:
    """
    Returns whether or not the user has voted on Top.gg. If there's no Top.gg token provided then this will always return `False`.
    This method doesn't handle timeouts; you are expected to implement them yourself.
    """

    # Try and see whether the user has voted
    url = f"https://top.gg/api/bots/{bot.user.id}/check"
    session: aiohttp.ClientSession = aiohttp.ClientSession()
    
    async with session.get(url, params={"userId": user_id}, headers={"Authorization": config["dbl"]["TOKEN"]}) as r:
        try:
            data = await r.json()
        except Exception:
            await session.close()
            return False
        if r.status != 200:
            await session.close()
            return False
    
    await session.close()
    return data.get("voted", False)


class HasNoPP(commands.CheckFailure):
    """The generic error for when a user doesn't have a pp"""
    
class HasPP(commands.CheckFailure):
    """The generic error for when a user has a pp"""
    
class ItemRequired(commands.CheckFailure):
    """The generic error for when a user doesn't have an item"""


def has_pp() -> bool:
    async def predicate(ctx:commands.Context):
        if await Pp(ctx.author.id).check():
            return True
        raise HasNoPP(f"you need a pp first! Get one using `pp new`!")
    return commands.check(predicate) 

def has_no_pp() -> bool:
    async def predicate(ctx:commands.Context):
        if not await Pp(ctx.author.id).check():
            return True
        raise HasPP(f"you already have a pp, so you can't use this command.")
    return commands.check(predicate)