import typing

from discord.ext import commands


class IsNotSlashCommand(commands.CheckFailure):
    """
    The generic error for the bot failing the :func:`utils.checks.is_slash_command` check.
    """

    def __init__(self, ctx: commands.Context) -> None:
        self.ctx = ctx
        super().__init__(
            f"`{ctx.clean_prefix}{ctx.command.name}` must be used as a slash command. Try `/{ctx.command.name}`."
        )


def is_slash_command():
    """
    The check for whether or not the command is being used as a slash command (as
    defined by `ctx` being an instance of :class:`discord.ext.commands.SlashContext`).

    Raises:
        `IsNotSlashCommand`: If the command isn't being used in a slash command.
    """

    async def predicate(
        ctx: typing.Union[commands.Context, commands.SlashContext]
    ) -> bool:
        if isinstance(ctx, commands.SlashContext):
            return True
        raise IsNotSlashCommand(ctx)

    return commands.check(predicate)
