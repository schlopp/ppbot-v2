import random
import re

import discord
import toml


class AutoShardedClient(discord.AutoShardedClient):
    def __init__(self) -> None:
        super().__init__(
            status=discord.Status.idle, activity=discord.Game(name="There is no spoon")
        )

    async def on_message(self, message):
        if re.match(r"^(pp\s)(?!bo)", message.content, re.IGNORECASE):
            embed = discord.Embed()
            embed.title = random.choice(
                (
                    "Beep boop try again later.",
                    "I'm afraid I can't do that.",
                    "Bot broke, cry about it",
                    "Sorry, can't.",
                    "Nah.",
                )
            )
            embed.description = "pp bot is currently __offline__, and will be online again in a few days.\n[FAQ](https://github.com/schlopp/ppbot/blob/offline/FAQ.md)"
            await message.reply(embed=embed)


client = AutoShardedClient()
token = toml.load(r"config.toml")["token"]
client.run(token)
