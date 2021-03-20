import discord
from discord.ext import commands
import json, random, asyncio
import userdata as ud


class important(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['start', 'create', 'make'])
    @commands.bot_has_permissions(send_messages=True)
    async def new(self, ctx):
        async with ctx.typing():
            embed,pp,exception = await ud.create_embed(ctx,pp_adjective=True,pp_dependent=False)
            if exception:
                return await ud.handle_exception(ctx,exception)
            await pp.create()
            embed.description = f"{ctx.author.mention}, New pp created!"
        return await ctx.send(embed=embed)


    @commands.command(aliases=['display', 'view', 'inv', 'inventory', 'level', 'stats'])
    @commands.bot_has_permissions(send_messages=True)
    async def show(self, ctx, user:discord.Member=None):
        async with ctx.typing():
            embed,pp,user,exception = await ud.create_embed(ctx,user=user or ctx.author,return_user=True,include_tip=False)
            if exception:
                return await ud.handle_exception(ctx,exception)
            inv = ud.Inv(user.id)
            pp_size,pp_name,multiplier = await pp.pp_size(),await pp.pp_name(),await pp.multiplier()
            embed.title = f"{pp_name} ({user.display_name}'s pp)"
            embed.description = f"8{('='*int(pp_size/50))[:400] if pp_size else ''}D"
            embed.add_field(name="Stats", value=f"{pp_size} inches, {multiplier}x multiplier")
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
    async def grow(self, ctx):
        async with ctx.typing():
            embed,pp,exception = await ud.create_embed(ctx)
            if exception:
                return await ud.handle_exception(ctx,exception)
            growsize = random.randrange(1, 5)*await pp.multiplier()
            await pp.size_add(growsize)
            embed.description = f'{ctx.author.mention}, your pp grew **{growsize} inches!** It is now {await pp.pp_size()} inches. You can view your pp with the `pp show` command!'
        return await ctx.send(embed=embed)


    @commands.command(aliases=['name'], cooldown_after_parsing=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def rename(self, ctx):
        async with ctx.typing():
            embed,pp,exception = await ud.create_embed(ctx)
            if exception:
                return await ud.handle_exception(ctx,exception)
            embed.description = "What will your pp's new name be?"
        await ctx.send(embed=embed)
        def check(m):
            return m.author == ctx.author
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