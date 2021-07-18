import asyncio
import json
import random

import discord
import userdata as ud
from discord.ext import commands


class important(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['start', 'create', 'make'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @ud.has_no_pp()
    async def new(self, ctx):
        async with ctx.typing():
            ppname = 'Personal Pet' if await ud.has_sfw_mode(getattr(ctx.guild, 'id', 1))  else 'pp'
            embed = await ud.create_embed(ctx)
            await ud.Pp(ctx.author.id).create()
            embed.description = f"{ctx.author.mention}, New {ppname} created!"
        return await ctx.send(embed=embed)


    @commands.command(aliases=['display', 'view', 'inv', 'inventory', 'level', 'stats'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @ud.has_pp()
    async def show(self, ctx, user:discord.Member=None):
        async with ctx.typing():
            sfwmode = await ud.has_sfw_mode(getattr(ctx.guild, 'id', 1))
            ppname = 'Personal Pet' if sfwmode else 'pp'
            embed = await ud.create_embed(ctx, include_tip=False)
            
            if user:
                pp = await ud.Pp.fetch(user.id, self.bot)
                if not pp:
                    return await ud.handle_exception(ctx,f'{user.mention} doesn\'t have a {ppname}.')
            else:
                user = ctx.author
                pp = await ud.Pp.fetch(user.id, self.bot)
                
            embed.title = f"{pp.name} ({user.display_name}'s {ppname})"
            if user.id == 339170260064141322:
                embed.add_field(name='MED!?',value='WOAH. I JUST REALISED THE USER YOU\'RE TALKING ABOUT IS ACTUALLY MED. THIS IS SO COOL I LOVE MED AND ALL HER SUPPORT FOR ME.')
            elif user.id == 351762383351447553:
                embed.add_field(name='SCAMMER RANK', value='Honestly, I fucking hate you noah. How the fuck did you get three blackjacks in a row AND double king? I\'m crying right now and it\'s your fault. Thanks.')

            if sfwmode:
                length = pp.size // 100
                dog = [
                    f'  __  {(" " * length)[:20]}   _',
                    f'o\'\')}}_{("_" * length)[:20]}__//',
                    f' ` _/ {(" " * length)[:20]}   )',
                    f' (_(_/{("-" * length)[:20]}(_/',
                ]
                embed.description = "```\n{}```".format("\n".join(dog))
            else:
                embed.description = f"8{('='*(pp.size//50))[:400] if pp.size else ''}D"
                
            if pp.multiplier["voted"]:
                embed.add_field(name="Stats", value=f"{pp.size} inches\n~~{pp.default_multiplier}x multiplier~~ **[VOTER REWARD BONUS! {pp.multiplier['multiplier']}x MULTIPLIER](https://top.gg/bot/735147633076863027/vote)**")
            else:
                embed.add_field(name="Stats", value=f"{pp.size} inches\n{pp.multiplier['multiplier']}x multiplier **[You're currently missing out on a VOTER REWARD BONUS! Vote now to get a {pp.multiplier['multiplier']*2}x multiplier!](https://top.gg/bot/735147633076863027/vote)**")
            invlist = []
            async with ud.Inv(user.id) as inv:
                for item, amount in inv.items():
                    if amount > 0:
                        invlist.append(f"{item}: **{amount}**")
            if invlist:
                embed.add_field(name="Inventory", value="\n".join(invlist))
            embed.set_footer(text=f"give your {ppname} a name with \"pp rename\"")
        return await ctx.send(embed=embed)


    @commands.command(aliases=['upgrade', 'enlarge', '🆙'], cooldown_after_parsing=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @ud.has_pp()
    async def grow(self, ctx):
        async with ctx.typing():
            ppname = 'Personal Pet' if await ud.has_sfw_mode(getattr(ctx.guild, 'id', 1))  else 'pp'
            embed = await ud.create_embed(ctx)
            pp = await ud.Pp.fetch(ctx.author.id, self.bot)
            growsize = random.randint(1, 5) * pp.multiplier["multiplier"]
            pp.size += growsize
            embed.description = f'{ctx.author.mention}, your {ppname} grew **[{growsize}](https://www.youtube.com/watch?v=FP23VU01fz8) inches!**'
            await pp.update()
        return await ctx.send(embed=embed)


    @commands.command(aliases=['name'], cooldown_after_parsing=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @ud.has_pp()
    async def rename(self, ctx):
        async with ctx.typing():
            ppname = 'Personal Pet' if await ud.has_sfw_mode(getattr(ctx.guild, 'id', 1))  else 'pp'
            embed = await ud.create_embed(ctx)
            pp = await ud.Pp.fetch(ctx.author.id)
            embed.description = f"What will your {ppname}'s new name be?"
        await ctx.send(embed=embed)
        check = lambda m: m.author == ctx.author
        try:
            x = await self.bot.wait_for('message', timeout=45.0, check=check)
            if x:
                async with ctx.typing():
                    newname = x.content
                    if len(newname) > 32:
                        embed.description = f"{ctx.author.mention}, that name is too big! (32 characters max)"
                        return await ctx.send(embed=embed)
                    pp.name = newname
                    await pp.update()
                    embed.description = f"{ctx.author.mention}, your {ppname}'s name is now **{newname}**"
                return await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            async with ctx.typing():
                return await ctx.send(f"{ctx.author.mention}, time's up for changing name! Type faster next time")


def setup(bot):
    bot.add_cog(important(bot))
