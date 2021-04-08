import discord
import traceback
import sys
from discord.ext import commands


class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
            
        neatly stolen from https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612
        """

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return
        
        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')
        
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be used in DMs.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(colour=discord.Colour(0xff0000))
            embed.title = f"Oopsie {ctx.author.display_name},"
            embed.description = f"Make sure you use numbers and words in the correct places"
            embed.add_field(name="example:",value="`pp buy 10 fishing rod` ✅\n`pp show @obama` ✅\n`pp buy AAAAAAAAA fishing rod` ❌\n`pp show WAEDFSEWFSFEAWFEAW` ❌")
            return await ctx.send(embed=embed)
            
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(colour=discord.Colour(0xff0000))
            embed.title = f"Bro, slow down"
            embed.description = f"You can use this command again in **{round(error.retry_after, 1)} seconds**.\nBe patient {ctx.author.mention}"
            return await ctx.send(embed=embed)
        
        elif isinstance(error, commands.BotMissingPermissions):
            try:
                return await ctx.send(f"**Oopsie {ctx.author.display_name},** The command you're trying to use requires the permission to send links. Ask and admin to change pp bot's permissions.")
            except:
                pass
            
        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            embed = discord.Embed(colour=discord.Colour(0xff0000))
            embed.title = f"Oopsie {ctx.author.display_name},"
            embed.description = str(error)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))