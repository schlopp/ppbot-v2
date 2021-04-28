import discord
from discord.ext import commands
import userdata as ud

import asyncio
import random


class important(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self,ctx):
        async with ctx.typing():
            await asyncio.sleep(.1)
        await ctx.send('Yep it works')
    
    
    @commands.command(aliases=['sfwtoggle','sfw_toggle','familyfriendlymode','familyfriendly_mode','family_friendly_mode','togglesfw'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def sfwmode(self, ctx):
        sfw_mode = await ud.has_sfw_mode(ctx.guild.id)
        await ud.toggle_sfw_mode(ctx.guild.id)
        if sfw_mode:
            return await ctx.send(embed=discord.Embed(description='Disabled family friendly mode!'))
        return await ctx.send(embed=discord.Embed(description='Enabled family friendly mode!'))
    
    
    @commands.command(aliases=['top','lb'])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @ud.has_pp()
    async def leaderboard(self, ctx, user:discord.Member=None):
        async with ctx.typing():
            ppname = 'Personal Pet' if await ud.has_sfw_mode(ctx.guild.id) else 'pp'
            embed = await ud.create_embed(ctx, include_tip=False)
            if user:
                pp = await ud.Pp.fetch(user.id)
                if not pp:
                    return await ud.handle_exception(ctx,f'{user.mention} doesn\'t have a {ppname}.')
                user = user
            else:
                user = ctx.author
                pp = await ud.Pp.fetch(user.id)
            fetched = await ud.fetch('*','userdata.pp')
            fetched = sorted(fetched, key=lambda i:i['pp_size'])
            fetched.reverse()
            
            if await ud.has_sfw_mode(ctx.guild.id):
                embed.description = f'This server is on SFW mode. Showing the names of the top 10 {ppname}s is disabled.'
                position = 1
                for i in fetched[:10]:
                    member = ctx.guild.get_member(i["user_id"])
                    embed.add_field(
                        name=f'{position}. {f" ({member.display_name})" if member else ""}',
                        value=f'{ud.human_format(i["pp_size"])} inches',inline=False,
                        )
                    position += 1
            else:
                position = 1
                for i in fetched[:10]:
                    member = ctx.guild.get_member(i["user_id"]) if ctx.guild else None
                    embed.add_field(
                        name=f'{position}. {i["pp_name"]}{f" ({member.display_name})" if member else ""}',
                        value=f'{ud.human_format(i["pp_size"])}  inches',inline=False,
                        )
                    position += 1
            try:
                position = [i["user_id"] for i in fetched].index(pp.user_id) + 1
                if position == 1:
                    lead = "in first place!"
                else:
                    front = [i["user_id"] for i in fetched].index(pp.user_id)
                    difference = fetched[front - 1]["pp_size"] - fetched[position - 1]["pp_size"]
                    lead = f"{difference} inches behind {front}."
                embed.set_footer(text=f'{user.display_name if user.id != ctx.author.id else "Your"} position on the leaderboard: {position}. {lead}')
            except ValueError:
                pass
        return await ctx.send(embed=embed)
    
    
    @commands.command(aliases=['suggestion',])
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def suggest(self, ctx, *, suggestion:str):
        async with ctx.typing():
            channel = self.bot.get_channel(816777533089513490)
            embed = discord.Embed()
            embed.description = suggestion
            embed.set_footer(text=f'Suggestion from {ctx.author} ({ctx.author.id})')
            message = await channel.send(embed=embed)
            await message.add_reaction('👍')
            await message.add_reaction('👎')
        await ctx.send('Thank you for your suggestion.')
    
    
    @commands.command(aliases=['%','percent'])
    @commands.bot_has_permissions(send_messages=True)
    async def percentage(self, ctx, *, thing:str):
        async with ctx.typing():
            embed = discord.Embed()
            embed.title = f'{ctx.author.display_name}\'s {thing} percentage'
            embed.description = f'**{random.randint(0,100)}%** {thing}'
        await ctx.send(embed=embed)
    
    
    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.cooldown(1, 60*15, commands.BucketType.user)
    @ud.has_pp()
    async def donate(self, ctx, user:discord.Member, amount):
        async with ctx.typing():
            ppname = 'Personal Pet' if await ud.has_sfw_mode(ctx.guild.id) else 'pp'
            embed = await ud.create_embed(ctx)
            pp = await ud.Pp.fetch(ctx.author.id, self.bot)
            pp2 = await ud.Pp.fetch(user.id, self.bot)
            amount = pp.size if amount == "all" else int(amount)
            
            if pp.size < amount:
                return await ud.handle_exception(ctx,f"your pp isnt big enough! You need **{amount} inches** to donate this amount!")

            maxamount = 10 ** 4 if pp.multiplier["voted"] else 10 ** 3

            if amount > maxamount or amount < 1:
                return await ud.handle_exception(ctx,f"you cant donate that ammount! At most you can donate **{ud.human_format(maxamount)} inches. [VOTERS CAN DONATE UP TO 10K!](https://top.gg/bot/735147633076863027)**")

            if user == ctx.author:
                return await ud.handle_exception(ctx,'That\'s some tax evasion type shit')
            
            if not pp2:
                return await ud.handle_exception(ctx,f'{user.mention} doesn\'t have a {ppname}.')
            
            pp.size -= amount
            pp2.size += amount
            await pp.update()
            await pp2.update()

            embed.title = f'Donation completed! {amount} given.'
            embed.description = f'Your {ppname} is now **{pp.size} inches.** **{user.display_name}**\'s {ppname} is now **{pp2.size} inches!**'
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(important(bot))
