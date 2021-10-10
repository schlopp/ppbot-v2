import asyncio
import os
import random
import typing

import toml

import discord
from discord.ext import commands, tasks, vbu

from . import utils


class GamblingCommands(vbu.Cog):
    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.bot: vbu.Bot

    @commands.command(name="blackjack")
    @vbu.checks.bot_is_ready()
    @commands.bot_has_permissions(
        embed_links=True,
        read_messages=True,
        send_messages=True,
        use_external_emojis=True,
    )
    @commands.has_permissions(
        read_messages=True,
        send_messages=True,
        use_slash_commands=True,
    )
    async def _blackjack_command(self, ctx: commands.SlashContext):
        game = utils.BlackjackGame(utils.Deck())

        with vbu.Embed() as embed:
            embed.colour = 0x2C82C9
            kwargs = {"name": f"{ctx.author.name}'s game of Blackjack"}
            if ctx.author.avatar:
                kwargs["icon_url"] = ctx.author.avatar.url
            embed.set_author(**kwargs)
            embed.add_field(
                name=f"{ctx.author.name} 🎮",
                value=f"Hand - {game.player}\nTotal - `{game.player.total_value()}`",
            )
            embed.add_field(
                name="Pp bot <:ppevil:871396299830861884>",
                value=f"Hand - {game.dealer}\nTotal - `{game.dealer.total_value()}`",
            )

        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Hit", custom_id="HIT", style=discord.ui.ButtonStyle.primary
                ),
                discord.ui.Button(
                    label="Stand",
                    custom_id="STAND",
                    style=discord.ui.ButtonStyle.primary,
                ),
            )
        )

        if game.state == utils.BlackjackState.PLAYER_BLACKJACK:
            with embed:
                embed.colour = utils.GREEN
                embed.description = f"**BLACKJACK!**\n{ctx.author.name} walks away with {{REWARD}} (50% bonus)"
            await ctx.interaction.edit_original_message(
                embed=embed, components=components.disable_components()
            )

        elif game.state == utils.BlackjackState.DEALER_BLACKJACK:
            with embed:
                embed.colour = utils.RED
                embed.description = (
                    f"**DEALER BLACKJACK!**\n{ctx.author.name} loses {{REWARD}}"
                )
            await ctx.interaction.edit_original_message(
                embed=embed, components=components.disable_components()
            )

        elif game.state == utils.BlackjackState.PUSH:
            with embed:
                embed.colour = utils.YELLOW
                embed.description = (
                    f"**PUSH!**\nSomehow you both got a blackjack LMAO, it's a tie"
                )
            await ctx.interaction.edit_original_message(
                embed=embed, components=components.disable_components()
            )

        await ctx.interaction.response.send_message(embed=embed, components=components)

        original_message: discord.InteractionMessage = (
            await ctx.interaction.original_message()
        )

        actions: typing.List[str] = []

        def formatted_actions() -> str:
            print(actions)
            if not actions:
                return ""
            reversed_actions = list(reversed(actions))
            if len(actions) > 2:
                return "```diff\n{}\n{} previous {}...```".format(
                    "\n".join(reversed_actions[:2]),
                    len(reversed_actions) - 2,
                    "actions" if len(reversed_actions) - 3 else "action",
                )
            return "```diff\n{}```".format("\n".join(reversed_actions))

        def action_check(action_interaction: discord.Interaction) -> bool:
            if (
                action_interaction.message.id != original_message.id
                or action_interaction.user != ctx.author
            ):
                return

            if not hasattr(
                utils.BlackjackAction, action_interaction.data.get("custom_id", "")
            ):
                self.bot.loop.create_task(
                    action_interaction.response.send_message(
                        content="Something went wrong lmao try using this command again with different button",
                        ephemeral=True,
                    )
                )
                raise asyncio.TimeoutError()
                return

            return True

        while game.state == utils.BlackjackState.PLAYER_TURN:
            try:
                action_interaction: discord.Interaction = await self.bot.wait_for(
                    "component_interaction", check=action_check, timeout=15
                )
            except asyncio.TimeoutError:
                game.state = utils.BlackjackState.TIMEOUT
                break

            action = getattr(
                utils.BlackjackAction, action_interaction.data["custom_id"]
            )

            game.player_action(action)

            if action == utils.BlackjackAction.HIT:
                actions.append(
                    f"+ {ctx.author.name} hits and received a {game.player.cards[-1]}."
                )
            elif action == utils.BlackjackAction.STAND:
                actions.append(f"! {ctx.author.name} stands.")
            else:
                actions.append(f"? {ctx.author.name} {action.name.lower()}s.")

            with embed:
                embed.edit_field_by_index(
                    0,
                    name=f"{ctx.author.name} 🎮",
                    value=f"Hand - {game.player}\nTotal - `{game.player.total_value()}`",
                )
                embed.edit_field_by_index(
                    1,
                    name="Pp bot <:ppevil:871396299830861884>",
                    value=f"Hand - {game.dealer}\nTotal - `{game.dealer.total_value()}`",
                )
                embed.description = formatted_actions() or None

            await action_interaction.response.edit_message(embed=embed)

        # await ctx.send(f"--- DEALERS TURN --- {game.state}")
        if game.state == utils.BlackjackState.TIMEOUT:
            actions.append(f"- {ctx.author.name} doesn't respond.")
            with embed:
                embed.colour = utils.YELLOW
                embed.description = f"**TIMED OUT!**\nWhile {ctx.author.name} was AFK, the dealer ran away with his {{INPUT}}"
                if actions:
                    embed.description += formatted_actions()

        elif game.state == utils.BlackjackState.PLAYER_BUST:
            actions.append(f"- {ctx.author.name} busts.")
            with embed:
                embed.colour = utils.RED
                embed.description = f"**BUST!**\n{ctx.author.name} got a bit to greedy, and busted. You lose {{REWARD}}"
                if actions:
                    embed.description += formatted_actions()

        await original_message.edit(
            embed=embed, components=components.disable_components()
        )


def setup(bot: vbu.Bot):
    x = GamblingCommands(bot)
    bot.add_cog(x)
