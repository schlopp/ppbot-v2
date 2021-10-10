import typing

from discord.ext import commands


class IsBusy(commands.CheckFailure):
    """
    The generic error for the bot failing the :func:`utils.checks.is_not_busy` check.
    """

    def __init__(self, ctx: commands.SlashContext) -> None:
        self.ctx = ctx
        self.command_ctx = self.ctx.bot.commands_in_use[ctx.author.id]
        super().__init__(
            f"You're already busy with `/{self.command_ctx.command.name}`, slow down bruv"
        )


def is_not_busy():
    """
    The check for whether or not the author is busy with another command (as
    defined by `ctx.author.id` having a :class:`discord.ext.commands.SlashContext` linked to it in :dict:`ctx.bot.commands_in_use`).

    Raises:
        `IsBusy`: If the author is busy with another command.
    """

    async def predicate(ctx: commands.SlashContext) -> bool:
        if ctx.bot.commands_in_use.get(ctx.author.id, None):
            raise IsBusy(ctx)
        return True

    return commands.check(predicate)
