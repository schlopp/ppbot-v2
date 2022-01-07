import logging
import typing

import discord  # type: ignore
from discord.ext import commands, vbu  # type: ignore

from . import utils


class ReplyCommand(vbu.Cog):
    bot: vbu.Bot
    logger: logging.Logger

    @commands.command(
        name="reply",
        add_slash_command=True,
        param_descriptions={
            "content": "The content of your reply",
        },
        autocomplete_params=["location"],
    )
    @commands.bot_has_permissions(
        read_messages=True,
        send_messages=True,
    )
    @commands.has_permissions(
        read_messages=True,
        send_messages=True,
        use_slash_commands=True,
    )
    @utils.is_slash_command()
    @vbu.checks.bot_is_ready()
    async def _reply_command(
        self, ctx: commands.SlashContext, *, content: str
    ) -> typing.Any:
        """
        Used to send a follow-up message to pp bot, usually during a minigame.
        """

        self.bot.dispatch("reply", ctx)


def setup(bot: vbu.Bot):
    x = ReplyCommand(bot)
    bot.add_cog(x)
