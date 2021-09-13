import random
import re

import discord
import toml


class AutoShardedClient(discord.AutoShardedClient):
    status = discord.Status.idle

    async def on_message(self, message):
        if re.match(r"^(pp\s)", message.content, re.IGNORECASE):
            laughing = random.choice(['kek', 'keke', 'kekw', 'lmao', 'lmfao', 'lol'])
            await message.reply(f"Sorry, but pp bot is currently offline (The dev's PC died and is being fixed {laughing})")

client = AutoShardedClient()
token = toml.load(r"config.toml")["token"]
client.run(token)
