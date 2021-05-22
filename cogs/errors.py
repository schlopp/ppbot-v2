import discord
import traceback
import sys
from discord.ext import commands
import datetime


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
        if cog and cog._get_overridden_method(cog.cog_command_error) is not None:
            return

        ignored = (commands.CommandNotFound)

        #Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return
        
        #if isinstance(error, commands.CommandNotFound):
        #    return await ctx.send('pp bot is currently being updated. Join the support server for more information. discord.gg/H7Avd8c')
        
        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')
        
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be used in DMs.')
            except discord.HTTPException:
                pass
            finally:
                ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(colour=discord.Colour(0xff0000))
            embed.title = f"Oopsie {ctx.author.display_name},"
            embed.description = f"Make sure you use numbers and words in the correct places"
            embed.add_field(name="example:",value="`pp buy 10 fishing rod` ✅\n`pp show @obama` ✅\n`pp buy AAAAAAAAA fishing rod` ❌\n`pp show WAEDFSEWFSFEAWFEAW` ❌")
            await ctx.send(embed=embed)
            return ctx.command.reset_cooldown(ctx)
            
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(colour=discord.Colour(0xff0000))
            embed.title = f"Bro, slow down"
            
            td = datetime.timedelta(milliseconds=int(error.retry_after*1000))
            days = td.days
            hours, remainder = divmod(td.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            # If you want to take into account fractions of a second
            seconds += td.microseconds / 1e6
            
            time_left = f"{round(seconds, 1)} second" if round(seconds, 1) == 1.0 else f"{round(seconds, 1)} seconds"
            
            if minutes:
                time_left = f"{minutes} minute and {time_left}" if minutes == 1 else f"{minutes} minutes and {time_left}"
                for key, value in {'hours':hours,'days':days}.items():
                    if value:
                        time_left = f"{value} {key[:-1]}, {time_left}" if value == 1 else f"{value} {key}, {time_left}"
            
            embed.description = f"You can use this command again in **{time_left}**\nBe patient {ctx.author.mention}"
            return await ctx.send(embed=embed)
        
        elif isinstance(error, commands.BotMissingPermissions):
            try:
                await ctx.send(f"**Oopsie {ctx.author.display_name},** The command you're trying to use requires the permission to send links. Ask an admin to change pp bot's permissions.")
            except:
                pass
            finally:
                ctx.command.reset_cooldown(ctx)
            
        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            #traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            embed = discord.Embed(colour=discord.Colour(0xff0000))
            embed.title = f"Oopsie {ctx.author.display_name},"
            embed.description = str(error)
            await ctx.send(embed=embed)
            return ctx.command.reset_cooldown(ctx)

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))