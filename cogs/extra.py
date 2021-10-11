# pylint: disable=unused-variable
# pylint: enable=too-many-lines

import discord
from discord.ext import commands
import json, random, asyncio
import userdata as ud


class extra(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["hospital"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @ud.has_pp()
    async def surgery(self, ctx):
        embed = await ud.create_embed(ctx)
        pp = await ud.Pp.fetch(ctx.author.id, self.bot)

        if pp.size < 25 * pp.multiplier["multiplier"]:
            embed.description = f"{ctx.author.mention}, your pp isnt big enough! You need at least **{25 * pp.multiplier['multiplier']} inches** to get surgery!"
            return await ctx.send(embed=embed)

        growsize = random.randrange(5, 14) * pp.multiplier["multiplier"]
        embed.title = "HOSPITAL"
        embed.description = (
            f"{ctx.author.mention} goes to the hospital for some pp surgery..."
        )

        if random.randrange(1, 10) > 2:  # 20% chance
            pp.size += growsize
            status = "SUCCESSFUL"
            message = f"The operation was successful! Your pp gained {growsize} inches! It is now {pp.size} inches."
        else:
            pp.size -= growsize
            status = "FAILED"
            message = f"The operation failed. Your pp snapped and you lost **{growsize} inches.** 😭 It is now {pp.size} inches."

        await pp.update()
        embed.add_field(name=status, value=message)
        return await ctx.send(embed=embed)

    @commands.command(aliases=["pray"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @ud.has_pp()
    async def beg(self, ctx):
        embed = await ud.create_embed(ctx)
        pp = await ud.Pp.fetch(ctx.author.id, self.bot)

        quote = random.choice(
            [
                "ew poor",
                "don't touch my pp",
                "my wife has a bigger pp than you",
                "broke ass bitch",
                "cringe poor",
                "beg harder",
                "poor people make me scared",
                "dont touch me poor person",
                "get a job",
                "im offended",
                "no u",
                "i dont speak poor",
                "you should take a shower",
                "i love my wife... i love my wife... i love my wife..",
                "drink some water",
                "begone beggar",
                "No.",
                "no wtf?",
                'try being a little ""cooler" next time',
            ]
        )
        combo = {
            "obama": quote,
            "roblox noob": quote,
            "dick roberts": quote,
            "johnny from johnny johnny yes papa": quote,
            "shrek": quote,
            "caleb": quote,
            "bob": quote,
            "walter": quote,
            "napoleon bonaparte": quote,
            "bob ross": quote,
            "coco": quote,
            "thanos": random.choice(
                ["begone before i snap you", "i'll snap ur pp out of existence"]
            ),
            "don vito": quote,
            "bill cosby": random.choice(
                [
                    "dude im a registered sex offender what do you want from me",
                    "im too busy touching people",
                ]
            ),
            "your step-sis": "i cant give any inches right now, im stuck",
            "pp god": "begone mortal",
            "random guy": quote,
            "genie": "rub me harder next time 😩",
            "the guy u accidentally made eye contact with at the urinal": "eyes on your own pp man",
            "your mom": random.choice(
                ["you want WHAT?", "im saving my pp for your dad"]
            ),
            "ur daughter": quote,
            "Big Man Tyrone": "Every 60 seconds in Africa a minute passes.",
            "speed": quote,
        }
        responce = random.choice(list(combo.items()))
        if random.randrange(0, 5) != 1:
            donation_amount = random.randrange(1, 10) * pp.multiplier["multiplier"]
            pp.size += donation_amount
            embed.description = f"**{responce[0]}** donated {donation_amount} inches to {ctx.author.mention}"
        else:
            embed.description = f"**{responce[0]}:** {responce[1]}"
        await ctx.send(embed=embed)
        return await pp.update()


def setup(bot):
    bot.add_cog(extra(bot))
