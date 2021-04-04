import discord
from discord.ext import commands
import userdata as ud

import asyncio


class important(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self,ctx):
        async with ctx.typing():
            await asyncio.sleep(.1)
        await ctx.send('Yep it works')
    
    
    @commands.command(aliases=['top','lb'])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def leaderboard(self, ctx, user:discord.Member=None):
        async with ctx.typing():
            fetched = await ud.fetch('*','userdata.pp')
            fetched = sorted(fetched, key=lambda i:i['pp_size'])
            fetched.reverse()
            
            embed,pp,user,exception = await ud.create_embed(ctx,
                user=user or ctx.author,
                return_user = True,
                include_tip = False
                )
            if exception:
                return await ud.handle_exception(ctx,exception)
            
            position = 1
            for i in fetched[:10]:
                if ctx.guild:
                    member = ctx.guild.get_member(i["user_id"]) if ctx.guild else None
                embed.add_field(name=f'{position}. {i["pp_name"]}{f" ({member.display_name})" if member else ""}',value=f'{i["pp_size"]} inches',inline=False)
                position+=1
            try:
                position = [i["user_id"] for i in fetched].index(pp.user_id)+1
                if position == 1:
                    lead = f"in first place!"
                else:
                    front = [i["user_id"] for i in fetched].index(pp.user_id)
                    difference = fetched[front-1]["pp_size"]-fetched[position-1]["pp_size"]
                    lead = f"{difference} inches behind {front}."
                embed.set_footer(text=f'{user.display_name or "Your"} position on the leaderboard: {position}. {lead}')
            except ValueError:
                pass
        return await ctx.send(embed=embed)
    
    
    @commands.command(aliases=['suggestion',])
    @commands.cooldown(1, 30, commands.BucketType.user)
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


def setup(bot):
    bot.add_cog(important(bot))
