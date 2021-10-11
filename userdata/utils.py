import asyncpg
import discord
import toml
import aiohttp
import random
from userdata import Pp
from discord.ext import commands
import re

with open("./config.toml") as f:
    config = toml.loads(f.read())


class SQLMethodError(Exception):
    """SQL Method Error"""

    def __init__(self, method):
        self.method = method
        super().__init__("SQL Method unkown")

    def __str__(self):
        return f'SQL Method: "{self.method}" unknown\033[0m'


async def fetch(pgselect: str, pgfrom: str, pgwhere: str = None):
    """returns the return value of a fetched premade-sql statement\n\n__\n\nsql statement:\n\n- `SELECT {pgselect} FROM {pgfrom}( WHERE {pgwhere}; || ;  )`"""
    pgwhere = " WHERE {pgwhere};" if pgwhere else f";"
    conn = await asyncpg.connect(config["admin"]["PSQL"])
    fetched = await conn.fetch(
        f"""
        SELECT {pgselect} FROM {pgfrom}{pgwhere}
        """
    )
    await conn.close()
    return [dict(i) for i in fetched]


async def runsql(method: str, sqlstring: str):
    conn = await asyncpg.connect(config["admin"]["PSQL"])
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


async def create_embed(ctx: commands.Context, **kwargs):
    """
    kwargs:
    include_tip - `bool` (default True)\n
    """
    embed: discord.Embed = discord.Embed(
        colour=discord.Colour(random.choice([0x008000, 0xFFA500, 0xFFFF00]))
    )
    include_tip: bool = kwargs.get("include_tip", True)
    if include_tip and random.randint(1, 10) == 1:
        embed.add_field(
            name="TIP:",
            value=random.choice(
                [
                    "Tools in the shop unlock commands!",
                    "There's a small chance of an event happening upon using a command!",
                    "You can see the leaderboard by using the `pp leaderboard` command!",
                    "There are a ton of fun commands! Have you tried them yet?",
                    "[Invite my friend's pigeon pet bot!](https://top.gg/bot/753013667460546560)",
                    "Join the official pp bot server! use `pp support`",
                    "Add pp bot to your server! use `pp invite`",
                    "[Voting gives you a 2x boost and other perks!](https://top.gg/bot/735147633076863027/vote)",
                ]
            ),
        )
    return embed


async def handle_exception(ctx: commands.Context, exception: str):
    embed = discord.Embed(colour=discord.Colour(0xFF0000))
    embed.title = f"Oopsie {ctx.author.display_name}, something went wrong."
    embed.description = exception
    return await ctx.send(embed=embed)


async def get_user_topgg_vote(bot, user_id: int) -> bool:
    """
    Returns whether or not the user has voted on Top.gg. If there's no Top.gg token provided then this will always return `False`.
    """

    # Try and see whether the user has voted
    url = f"https://top.gg/api/bots/{bot.user.id}/check"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            params={"userId": user_id},
            headers={"Authorization": config["dbl"]["TOKEN"]},
        ) as r:
            try:
                data = await r.json()

            except Exception:
                return False

            if r.status != 200:
                return False

    return bool(data.get("voted", False))


class HasNoPP(commands.CheckFailure):
    """The generic error for when a user doesn't have a pp"""


class HasPP(commands.CheckFailure):
    """The generic error for when a user has a pp"""


class ItemRequired(commands.CheckFailure):
    """The generic error for when a user doesn't have an item"""


class ShopItemNotFound(commands.CheckFailure):
    """The generic error for when a item doesnt exist"""


class AmountNotEnough(commands.CheckFailure):
    """The generic error for when a amount isn't enough"""


def has_pp() -> bool:
    async def predicate(ctx: commands.Context):
        if await Pp.fetch(ctx.author.id, get_multiplier=False):
            return True
        raise HasNoPP(f"you need a pp first! Get one using `pp new`!")

    return commands.check(predicate)


def has_no_pp() -> bool:
    async def predicate(ctx: commands.Context):
        if not await Pp.fetch(ctx.author.id, get_multiplier=False):
            return True
        raise HasPP(f"you already have a pp, so you can't use this command.")

    return commands.check(predicate)


async def has_sfw_mode(guild_id: int) -> bool:
    conn = await asyncpg.connect(config["admin"]["PSQL"])
    fetched = await conn.fetch(
        """SELECT sfw FROM userdata.server_settings WHERE guild_id = $1""", guild_id
    )
    if not fetched:
        await conn.execute(
            """INSERT INTO userdata.server_settings(guild_id) VALUES($1) ON CONFLICT (guild_id) DO NOTHING;""",
            guild_id,
        )
        fetched = await conn.fetch(
            """SELECT sfw FROM userdata.server_settings WHERE guild_id = $1""", guild_id
        )
    await conn.close()
    if dict(fetched[0])["sfw"]:
        return True
    return False


async def toggle_sfw_mode(guild_id: int):
    if await has_sfw_mode(guild_id):
        conn = await asyncpg.connect(config["admin"]["PSQL"])
        await conn.execute(
            """UPDATE userdata.server_settings SET sfw = false WHERE guild_id = $1;""",
            guild_id,
        )
        return await conn.close()
    conn = await asyncpg.connect(config["admin"]["PSQL"])
    await conn.execute(
        """UPDATE userdata.server_settings SET sfw = true WHERE guild_id = $1;""",
        guild_id,
    )
    await conn.close()


def human_format(num: int):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."), ["", "K", "M", "B", "T"][magnitude]
    )


def deepdict(o):
    if hasattr(o, "__dict__"):
        o = vars(o)

    elif isinstance(o, asyncpg.Record):
        o = dict(o)

    if isinstance(o, dict):
        {key: deepdict(value) for key, value in o.items()}

    elif isinstance(o, list):
        o = [deepdict(i) for i in o]

    return o


def clean_code(code: str):
    if re.search(r"^```(.|\s)*```$", code):
        return code.split("\n", 1)[1].strip()[:-3]
    if re.search(r"^`.*`$", code):
        return code.strip()[1:-1]
    return code.strip()
