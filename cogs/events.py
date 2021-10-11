import asyncio
import discord
import random
import re
import userdata as ud
from discord.ext import commands


class CEvents(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.events = {}

    def new_event(self, channel_id: int, answer: str):
        if channel_id in self.events:
            self.events[channel_id][answer] = {
                "first": None,
                "second": None,
                "third": None,
            }

        else:
            self.events[channel_id] = {
                answer: {
                    "first": None,
                    "second": None,
                    "third": None,
                }
            }

        return self.events[channel_id][answer]

    @commands.Cog.listener()
    async def on_command(self, ctx):
        await ud.runsql(
            "execute",
            """UPDATE userdata.stats SET commands_run = userdata.stats.commands_run + 1""",
        )

        if random.randint(1, 200) != 1:
            return  # 0.5% chance

        await asyncio.sleep(1)
        string = random.choice(
            [
                "pp bot time",
                "tax evasion",
                "frog",
                "peepee poopoo",
                "gambling addiction",
                "cool kids",
                "human rights",
                "happy flour",
                "orphan",
                "big pp",
            ]
        )

        event = self.new_event(ctx.channel.id, string[::-1])
        embed = discord.Embed(
            colour=discord.Colour(random.choice([0x008000, 0xFFA500, 0xFFFF00])),
            title="**EVENT**",
        )
        embed.description = "A random event has been triggered!"
        embed.add_field(name="Reverse!", value=f"Type **`{string}`** backwards")

        await ctx.send(embed=embed, delete_after=30)
        await asyncio.sleep(30)

        embed = discord.Embed(
            colour=discord.Colour(random.choice([0x008000, 0xFFA500, 0xFFFF00]))
        )
        if not event["first"]:
            embed.title = "nobody won lmaoooo"
        else:
            size = random.randint(50, 200)
            first = await ud.Pp.fetch(event["first"], get_multiplier=False)
            first.size += size * 3
            await first.update()

            embed.add_field(
                name="🥇 first place",
                value=f"{first.name} wins {size * 3} inches!",
                inline=False,
            )
            if event["second"]:
                second = await ud.Pp.fetch(event["second"], get_multiplier=False)
                second.size += size * 2
                await second.update()
                embed.add_field(
                    name="🥈 second place",
                    value=f"{second.name} wins {size * 2} inches!",
                    inline=False,
                )

            if event["third"]:
                third = await ud.Pp.fetch(event["third"], get_multiplier=False)
                third.size += size
                await third.update()
                embed.add_field(
                    name="🥉 third place",
                    value=f"{third.name} wins {size} inches!",
                    inline=False,
                )

        await ctx.send(embed=embed)
        try:
            self.events[ctx.channel.id].pop(string[::-1], None)
        except IndexError:
            pass

    @commands.Cog.listener()
    @commands.has_permissions(send_messages=True, embed_links=True)
    async def on_message(self, message):
        """
        Check if message is an answer for an event
        """

        if message.author.bot:
            return
        if message.channel.id not in self.events.keys():
            return
        if message.content.lower() not in self.events[message.channel.id].keys():
            return

        event = self.events[message.channel.id][message.content.lower()]
        author = message.author.id
        pp = await ud.Pp.fetch(author)

        if not pp:
            raise ud.HasNoPP(f"you need a pp first! Get one using `pp new`!")

        if author in event.values():
            await message.channel.send(
                f"{message.author.mention} dude you cant enter the compition twice lmao"
            )
            return

        if not event["first"]:
            event["first"] = author
        elif not event["second"]:
            event["second"] = author
        elif not event["third"]:
            event["third"] = author
        else:
            await message.channel.send(
                f"{message.author.mention} should've been faster"
            )
            return

        inverted = {value: key for key, value in event.items()}
        position = inverted[author]
        return await message.channel.send(
            f"{message.author.mention} got {position} place!"
        )


def setup(bot):
    bot.add_cog(CEvents(bot))
