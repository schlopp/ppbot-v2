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
    @commands.bot_has_permissions(send_messages=True)
    @ud.has_no_pp()
    async def new(self, ctx):
        async with ctx.typing():
            embed = await ud.create_embed(ctx)
            await ud.Pp(ctx.author.id).create()
            embed.description = f"{ctx.author.mention}, New pp created!"
        return await ctx.send(embed=embed)


    @commands.command(aliases=['display', 'view', 'inv', 'inventory', 'level', 'stats'])
    @commands.bot_has_permissions(send_messages=True)
    @ud.has_pp()
    async def show(self, ctx, user:discord.Member=None):
        async with ctx.typing():
            embed = await ud.create_embed(ctx, include_tip=False)
            if user:
                if not await ud.Pp(user.id).check():
                    return await ud.handle_exception(ctx,f'{user.mention} doesn\'t have a pp.')
                user = user
            else:
                user = ctx.author
            pp = ud.Pp(user.id)
            inv = ud.Inv(user.id)
            pp_size,pp_name,multiplier = await pp.pp_size(),await pp.pp_name(),await pp.multiplier(self.bot)
            embed.title = f"{pp_name} ({user.display_name}'s pp)"
            
            if await ud.has_sfw_mode(ctx.guild.id):
                length = pp_size//100
                dog:list = [
                    f'  __  {(" "*length)[:20]}   _',
                    f'o\'\')}}_{("_"*length)[:20]}__//',
                    f' ` _/ {(" "*length)[:20]}   )',
                    f' (_(_/{("-"*length)[:20]}(_/',
                ]
                embed.description = "```\n{}```".format("\n".join(dog))
            else:
                embed.description = f"8{('='*(pp_size//50))[:400] if pp_size else ''}D"
                
            if await ud.get_user_topgg_vote(self.bot, user.id):
                embed.add_field(name="Stats", value=f"{pp_size} inches\n~~{multiplier//2}x multiplier~~ **[VOTER REWARD BONUS! {multiplier}x MULTIPLIER](https://top.gg/bot/735147633076863027/vote)**")
            else:
                embed.add_field(name="Stats", value=f"{pp_size} inches\n{multiplier}x multiplier **[You're currently missing out on a VOTER REWARD BONUS! Vote now to get a {multiplier*2}x multiplier!](https://top.gg/bot/735147633076863027/vote)**")
            invlist = []
            items = await inv.fetch_all()
            for item, amount in items.items():
                if amount > 0:
                    invlist.append(f"{item}: **{amount}**")
            if invlist:
                embed.add_field(name="Inventory", value="\n".join(invlist))
            embed.set_footer(text="give your pp a name with \"pp rename\"")
        return await ctx.send(embed=embed)


    @commands.command(aliases=['upgrade', 'enlarge', '🆙'], cooldown_after_parsing=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    @ud.has_pp()
    async def grow(self, ctx):
        async with ctx.typing():
            embed = await ud.create_embed(ctx)
            pp = ud.Pp(ctx.author.id)
            growsize = random.randrange(1, 5)*await pp.multiplier(self.bot)
            await pp.size_add(growsize)
            embed.description = f'{ctx.author.mention}, your pp grew **{growsize} inches!**'
        return await ctx.send(embed=embed)


    @commands.command(aliases=['name'], cooldown_after_parsing=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    @ud.has_pp()
    async def rename(self, ctx):
        async with ctx.typing():
            embed = await ud.create_embed(ctx)
            pp = ud.Pp(ctx.author.id)
            embed.description = "What will your pp's new name be?"
        await ctx.send(embed=embed)
        check = lambda m: m.author == ctx.author
        try:
            x = await self.bot.wait_for('message', timeout=45.0, check=check)
            async with ctx.typing():
                newname = x.content
                if len(newname) > 32:
                    embed.description = f"{ctx.author.mention}, that name is too big! (32 characters max)"
                    return await ctx.send(embed=embed)
                await pp.rename(newname)
                embed.description = f"{ctx.author.mention}, your pp's name is now **{newname}**"
            return await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            async with ctx.typing():
                return await ctx.send(f"{ctx.author.mention}, time's up for changing name! Type faster next time")


def setup(bot):
    bot.add_cog(important(bot))
