import typing
from discord.ext import commands, vbu


class UsingCommand:
    def __init__(self, ctx: commands.SlashContext):
        self.ctx = ctx

    def __enter__(self):
        self.ctx.bot.commands_in_use[self.ctx.author.id] = self.ctx

    def __exit__(self, *args, **kwargs):
        self.ctx.bot.commands_in_use.pop(self.ctx.author.id)
