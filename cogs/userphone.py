import asyncio
import discord
import random
import re
import userdata as ud
from discord.ext import commands, tasks
import io
from pynput.keyboard import Key, Controller


class UserPhone(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.channels = [878354287862906942, 878354307672588390]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id not in self.channels:
            return

        other_channels = self.channels.copy()
        other_channels.remove(message.channel.id)

        for i in other_channels:
            await self.bot.get_channel(i).send(
                f"`{message.channel.name}` **{message.author.name}**#{message.author.discriminator} <:userphone:878355139746992128> {message.content}"
            )


def setup(bot):
    bot.add_cog(UserPhone(bot))
