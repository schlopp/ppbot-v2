import discord
from discord.ext import commands
import random
from decimal import Decimal
import userdata as ud



class errors(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    



    @commands.Cog.listener()
    @commands.bot_has_permissions(send_messages=True)
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(colour=discord.Colour(0xff0000))
        embed.title = f"Oopsie {ctx.author.display_name}, something went wrong."
        if isinstance(error, commands.CommandOnCooldown):
            embed.title = "Bro, slow down"
            embed.description = f"You can use this command again in **{round(error.retry_after, 1)} seconds**.\nBe patient {ctx.author.mention}"
            return await ctx.send(embed=embed)
        if isinstance(error, discord.errors.Forbidden) or isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.BadArgument):
            embed.description = f"Make sure you use numbers and words in the correct places"
            embed.add_field(name="example:",value="`pp buy 10 fishing rod` ✅\n`pp show @obama` ✅\n`pp buy AAAAAAAAA fishing rod` ❌\n`pp show WAEDFSEWFSFEAWFEAW` ❌")
            return await ctx.send(embed=embed)
        else:
            embed.description = f'{ctx.author.mention}, {error}'
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(errors(bot))
