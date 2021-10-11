import asyncio
import discord
import random
import re
import userdata as ud
from discord.ext import commands, tasks
import io
from pynput.keyboard import Key, Controller


class Mario(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_message(self, message: discord.Message):

    #     # has to be in ghigeon general chat
    #     general_chat_id = 879019536240767016
    #     if message.channel.id != general_chat_id:
    #         return

    #     # Get a sexy lil keyboard instance
    #     keyboard = Controller()
    #     print(2)

    #     # Let's jump!
    #     if message.content.lower() == 'jump' or message.content.lower() == 'j':
    #         print('jump')
    #         keyboard.press(Key.up)
    #         await asyncio.sleep(0.5)
    #         keyboard.release(Key.up)

    #     # To the left!
    #     if message.content.lower() == 'left' or message.content.lower() == 'l':
    #         print('left')
    #         keyboard.press(Key.left)
    #         await asyncio.sleep(1)
    #         keyboard.release(Key.left)

    #     # Or the right?
    #     if message.content.lower() == 'right' or message.content.lower() == 'r':
    #         print('right')
    #         keyboard.press(Key.right)
    #         await asyncio.sleep(1)
    #         keyboard.release(Key.right)


def setup(bot):
    bot.add_cog(Mario(bot))
