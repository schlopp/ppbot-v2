import asyncio
import logging
import random
import typing

import discord  # type: ignore
from discord.ext import commands, vbu  # type: ignore

from cogs.utils.gambling.cards import Value  # type: ignore

from . import utils


class WrongInput(Exception):
    def __init__(self, interaction: discord.Interaction, value: str, *args):
        super().__init__(*args)
        self.interaction = interaction
        self.value = value


class BegCommand(vbu.Cog):
    bot: vbu.Bot
    logger: logging.Logger

    async def play_fill_in_the_blank(
        self,
        ctx: vbu.SlashContext,
        *,
        cache: utils.CachedUser,
        location: utils.BeggingLocation,
        db: vbu.DatabaseConnection,
    ):
        """
        Run the fill-in-the-blank minigame.
        """

        with vbu.Embed() as embed:
            embed.colour = utils.BLUE
            embed.set_author(
                name=f"{ctx.author.display_name}'s minigame",
                icon_url=ctx.author.avatar.url,
            )
            embed.title = "Fill in the blank!"
            fill_in_the_blank = location.quotes.minigames.fill_in_the_blank

            prompt, answer = random.choice(
                [
                    (
                        "`Whoever threw that paper, your mom's a `{}`!`",
                        "HOE",
                    ),
                    (
                        "`I have the power of `{}` on my side!`",
                        "GOD AND ANIME",
                    ),
                    (
                        "`*dodges bullets like in The `{}`*`",
                        "MATRIX",
                    ),
                    ("`You'll never `{}` me alive! *doot*`", "TAKE"),
                    ("`Doin' your `{}", "MOM"),
                    (
                        "`Shut yo skin tone `{}` bone google chrome no home flip phone disowned ice "
                        "cream cone garden gnome extra chromosome metronome dimmadome head ass tf up`",
                        "CHICKEN",
                    ),
                    ("`WHY ARE YOU BUYING CLOTHES AT THE `{}` STORE?`", "SOUP"),
                ]
            )
            prompt = prompt.format(
                f"[`{' '.join(i if i == ' ' else '_' for i in answer)}`]({self.bot.hyperlink})"
            )

            embed.description = f"{fill_in_the_blank.context}\n\n**{fill_in_the_blank.approacher}:** {prompt}"
            embed.set_footer("/reply with the missing word")

        await utils.responses.send_or_edit_response(
            ctx.interaction, embed=embed, components=None
        )

        def reply_check(reply_ctx: vbu.SlashContext) -> bool:
            if reply_ctx.author != ctx.author or reply_ctx.channel != ctx.channel:
                return False

            try:
                value = reply_ctx.interaction.data["options"][0]["value"]
                if value.upper() == answer:
                    return True
                else:
                    raise WrongInput(reply_ctx.interaction, value)
            except (KeyError, IndexError):
                pass

            return False

        try:
            user_reply: commands.SlashContext = await self.bot.wait_for(
                "reply",
                check=reply_check,
                timeout=30.0,
            )

        except asyncio.TimeoutError:
            with embed:
                embed.title = "You suck at guessing"
                embed.description = (
                    f"The answer was [`{answer}`]({self.bot.hyperlink}), but you took way too long to respond."
                    f" You get {utils.format_rewards()}.\n\n**{fill_in_the_blank.approacher}:** {fill_in_the_blank.fail}"
                )
                embed.remove_footer()
            return await utils.responses.send_or_edit_response(
                ctx.interaction, embed=embed
            )

        except WrongInput as wrong_input:
            with embed:
                embed.title = "Beep boop you're wrong"
                embed.description = (
                    f"The answer was [`{answer.title()}`]({self.bot.hyperlink}), but you typed `{wrong_input.value}`. "
                    f"You get {utils.format_rewards()}.\n\n**{fill_in_the_blank.approacher}:** {fill_in_the_blank.fail}"
                )
                embed.remove_footer()

            return await wrong_input.interaction.response.send_message(
                f"**{wrong_input.interaction.user}:** “{wrong_input.value}”",
                embed=embed,
            )

        else:
            with vbu.Embed() as embed:
                embed.colour = utils.PINK

                # Set the embed's author
                embed.set_author(
                    name=f"{fill_in_the_blank.approacher} \N{bullet} Minigame Completed",
                )

                # Generate rewards and give them to the user
                loot = location.loot_table.get_random_loot(self.bot, boosted=True)
                async with utils.Inventory.fetch(
                    self.bot, db, ctx.author.id, update_values=True
                ) as inv:
                    inv.add_items(*loot)

                growth = int(random.randint(1000, 2000) * cache.pp.multiplier)
                cache.pp.size += growth

                # Get a random quote and format it with the reward
                quote = fill_in_the_blank.success.format(
                    utils.format_rewards(inches=growth, items=loot)
                )

                # Set the embed's description to the quote
                embed.description = f"“{quote}”"

            return await user_reply.interaction.response.send_message(
                f"**{user_reply.author}:** “{user_reply.interaction.data['options'][0]['value']}”",
                embed=embed,
            )

    @commands.command(
        name="beg",
        add_slash_command=True,
        cooldown_after_parsing=True,
        param_descriptions={
            "location": "The place you're begging_skill at",
        },
        autocomplete_params=["location"],
    )
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
    @utils.is_slash_command()
    @utils.is_not_busy()
    @vbu.checks.bot_is_ready()
    async def _beg_command(
        self, ctx: commands.SlashContext, location_name: typing.Optional[str] = None
    ) -> typing.Any:
        """
        Beg for some sweet sweet inches lmao
        """

        with utils.UsingCommand(ctx):
            async with vbu.DatabaseConnection() as db:

                cache: utils.CachedUser = await utils.get_user_cache(
                    ctx.author.id,
                    db=db,
                    bot=self.bot,
                    logger=self.logger,
                )
                begging_skill = cache.get_skill("BEGGING")

                if location_name is None:
                    location_name = cache.settings.get("current_begging_location")

                locations = utils.BeggingLocations(
                    begging_skill.level, *self.bot.begging["locations"]
                )

                # No location chosen in autocomplete and no default location set
                if location_name is None:

                    components = discord.ui.MessageComponents(
                        discord.ui.ActionRow(locations.to_select_menu())
                    )

                    with vbu.Embed() as embed:
                        embed.colour = utils.colours.BLUE
                        embed.set_author(
                            name=random.choice(
                                [
                                    "Where you begging at?",
                                    "Where are you begging?",
                                    "Where you begging?",
                                ]
                            )
                        )
                        embed.description = "\n".join(
                            (
                                "Btw, level the `Begging` skill to unlock new locations",
                                f"Current level: {utils.int_to_roman(begging_skill.level)}",
                            )
                        )

                    await ctx.interaction.response.send_message(
                        embed=embed, components=components
                    )

                    try:
                        original_message = await ctx.interaction.original_message()

                        def check(
                            interaction: discord.Interaction,
                        ) -> typing.Union[bool, None]:

                            # Check if the interaction is used the original context interaction message.
                            if (
                                interaction.message
                                and interaction.message.id != original_message.id
                            ):
                                return False

                            if interaction.user != ctx.author:
                                self.bot.loop.create_task(
                                    interaction.response.send_message(
                                        content="Bro this is not meant for you LMAO",
                                        ephemeral=True,
                                    )
                                )
                                return False

                            return True

                        # Wait for a response
                        payload: discord.Interaction = await self.bot.wait_for(
                            "component_interaction",
                            check=check,
                            timeout=15.0,
                        )

                    except asyncio.TimeoutError:
                        with embed:
                            embed.description = (
                                "**You took too long to respond, type faster bro**\n\n"
                                + embed.description
                            )
                        return await utils.responses.send_or_edit_response(
                            ctx.interaction,
                            embed=embed,
                            components=components.disable_components(),
                        )

                    # Get the selected location
                    location = locations.get_location_from_interaction(payload)

                    # Location not found?
                    if location is None:
                        return await utils.responses.send_or_edit_response(
                            ctx.interaction,
                            embed=discord.Embed(
                                title="Location not found",
                                description="Please try again",
                                colour=utils.colours.RED,
                            ),
                            components=components.disable_components(),
                        )

                else:
                    location = locations.get_location_from_id(location_name)
                    if location is None:
                        return await ctx.interaction.response.send_message(
                            "You have to pick one of the options lmao", ephemeral=True
                        )

                await cache.update_settings("current_begging_location", location.id)

                # 5% chance of fill in the blank minigame
                # if (random_percentage := random.random()) < 0.05:
                if random_percentage := random.random():
                    return await self.play_fill_in_the_blank(
                        ctx, cache=cache, location=location, db=db
                    )

                # 5% chance of scramble minigame
                elif random_percentage < 0.1:
                    with vbu.Embed() as embed:
                        embed.colour = utils.BLUE
                        embed.set_author(
                            name=f"{ctx.author.display_name}'s minigame",
                            icon_url=ctx.author.avatar.url,
                        )
                        embed.title = "Scramble!"
                        scramble = location.quotes.minigames.scramble

                        unscrambled = random.choice(
                            [
                                "bitch",
                                "peepee",
                                "balls",
                                "taxes",
                                "tax evasion",
                                "pp bot",
                                "multiplier",
                                "supercalifragilisticexpialidocious",
                                "amogus",
                                "testicles",
                                "karen",
                                "schlopp",
                                "i love balls",
                                "doin ur mom",
                                "try harder lmao",
                                "small cock",
                            ]
                        )

                        scrambled = utils.scramble(unscrambled)

                        embed.description = f"{scramble.context}\n\n{scramble.approacher}: [`{scrambled}`]({self.bot.hyperlink})"
                        embed.set_footer("Respond to this message with the answer")

                    await utils.responses.send_or_edit_response(
                        ctx.interaction,
                        embed=embed,
                        components=None,
                    )

                    attempts_left = 3

                    def scramble_check(message: discord.Message) -> bool:

                        if (
                            message.author != ctx.author
                            or message.channel != ctx.channel
                        ):
                            return False

                        if message.content.lower() != unscrambled.lower():
                            nonlocal attempts_left
                            attempts_left -= 1
                            self.bot.loop.create_task(
                                message.reply(
                                    f"That's not the correct answer lol. You have **{attempts_left} attempts** left"
                                )
                            )
                            if not attempts_left:
                                raise asyncio.TimeoutError
                            return False

                        return True

                    while attempts_left:
                        try:
                            await self.bot.wait_for(
                                "message",
                                check=scramble_check,
                                timeout=15.0,
                            )
                            break
                        except asyncio.TimeoutError:
                            with embed:
                                embed.description = f"You should work on your scrambling skills, the answer was `{unscrambled}`. You get {utils.format_rewards()}"
                            return await utils.responses.send_or_edit_response(
                                ctx.interaction, embed=embed
                            )

                    with vbu.Embed() as embed:
                        embed.colour = utils.PINK

                        # Generate rewards and give them to the user
                        loot = location.loot_table.get_random_loot(
                            self.bot, boosted=True
                        )
                        async with utils.Inventory.fetch(
                            self.bot, db, ctx.author.id, update_values=True
                        ) as inv:
                            inv.add_items(*loot)

                        growth = int(random.randint(1000, 2000) * cache.pp.multiplier)
                        cache.pp.size += growth

                        embed.description = f"**GG!** You win {utils.format_rewards(inches=growth, items=loot)}!"

                    # Update the message
                    return await utils.responses.send_or_edit_response(
                        ctx.interaction,
                        embed=embed,
                        components=None,
                    )

                # 5% chance of retype event
                elif random_percentage < 0.15:
                    with vbu.Embed() as embed:
                        embed.colour = utils.BLUE
                        embed.set_author(
                            name=f"{ctx.author.display_name}'s minigame",
                            icon_url=ctx.author.avatar.url,
                        )
                        embed.title = "Retype!"
                        retype = location.quotes.minigames.retype

                        # Get a random sentence
                        sentence = random.choice(retype.sentences)
                        uncopyable_sentence = utils.uncopyable(sentence)

                        embed.description = f"{retype.context}\n\nQuickly! Retype this sentence is chat: [`{uncopyable_sentence}`]({self.bot.hyperlink})"
                        embed.set_footer("Respond to this message with the sentence")

                    await utils.responses.send_or_edit_response(
                        ctx.interaction,
                        embed=embed,
                        components=None,
                    )

                    attempts_left = 3

                    def retype_check(message: discord.Message) -> bool:

                        if (
                            message.author != ctx.author
                            or message.channel != ctx.channel
                        ):
                            return False

                        if message.content.lower() != sentence.lower():
                            nonlocal attempts_left
                            attempts_left -= 1

                            if message.content == uncopyable_sentence:
                                self.bot.loop.create_task(
                                    message.reply(
                                        f"Did you really think you could get away with copy-pasting? LMAO, you have **{attempts_left} attempts** left"
                                    )
                                )
                            else:
                                self.bot.loop.create_task(
                                    message.reply(
                                        f"That's not the correct answer lol. You have **{attempts_left} attempts** left"
                                    )
                                )
                            if not attempts_left:
                                raise asyncio.TimeoutError
                            return False

                        return True

                    while attempts_left:
                        try:
                            await self.bot.wait_for(
                                "message",
                                check=retype_check,
                                timeout=30.0,
                            )
                            break
                        except asyncio.TimeoutError:
                            embed.description = f"Wow, you're a slow typer. You get {utils.format_rewards()}. Cry about it"
                            return await utils.responses.send_or_edit_response(
                                ctx.interaction, embed=embed
                            )

                    with vbu.Embed() as embed:
                        embed.colour = utils.PINK

                        # Generate rewards and give them to the user
                        loot = location.loot_table.get_random_loot(
                            self.bot, boosted=True
                        )
                        async with utils.Inventory.fetch(
                            self.bot, db, ctx.author.id, update_values=True
                        ) as inv:
                            inv.add_items(*loot)

                        growth = int(random.randint(1000, 2000) * cache.pp.multiplier)
                        cache.pp.size += growth

                        embed.description = f"**GG!** Nice typing skills bro, you win {utils.format_rewards(inches=growth, items=loot)}!"

                    # Update the message
                    return await utils.responses.send_or_edit_response(
                        ctx.interaction,
                        embed=embed,
                        components=None,
                    )

                else:
                    # Update database and build the embed for receiving a generic donation.
                    with vbu.Embed() as embed:
                        embed.colour = utils.BLUE
                        donators: utils.Donators = self.bot.begging["donators"]
                        donator = donators.get_random_donator()
                        if donator is None:
                            raise ValueError("No donators found.")

                        # Generate rewards and give them to the user
                        loot = location.loot_table.get_random_loot(self.bot)
                        async with utils.Inventory.fetch(
                            self.bot, db, ctx.author.id, update_values=True
                        ) as inv:
                            inv.add_items(*loot)

                        growth = int(random.randint(1, 50) * cache.pp.multiplier)
                        cache.pp.size += growth

                        # If there are any donator success quotes, use them
                        if donator.quotes.success:
                            quotes = donator.quotes.success

                        # Otherwise, use the default quotes
                        else:
                            quotes = location.quotes.success

                        # Get a random quote and format it with the reward
                        quote = random.choice(quotes).format(
                            utils.format_rewards(inches=growth, items=loot)
                        )

                        # Set the embed's author
                        embed.set_author(
                            name=f"{donator.name} \N{bullet} {location.name}",
                            icon_url=donator.icon_url or embed.Empty,
                        )

                        # Set the embed's description to the quote
                        embed.description = f"“{quote}”"

                    # Update the message
                    await utils.responses.send_or_edit_response(
                        ctx.interaction,
                        embed=embed,
                        components=None,
                    )

    @_beg_command.autocomplete
    async def _beg_autocomplete(
        self, ctx: commands.SlashContext, interaction: discord.Interaction
    ) -> typing.Any:
        """
        Autocomplete coroutine, responsible for sending the list of locations
        """

        try:
            async with vbu.DatabaseConnection() as db:
                cache: utils.CachedUser = await utils.get_user_cache(
                    ctx.author.id,
                    db=db,
                    bot=self.bot,
                    logger=self.logger,
                )
                begging_skill = cache.get_skill("BEGGING")
                locations = utils.BeggingLocations(
                    begging_skill.level, *self.bot.begging["locations"]
                )

                # try:
                #     value: str = interaction.data["options"][0]["value"]

                # # Somehow no options were passed, so just default to an empty string
                # except (AttributeError, IndexError, KeyError):
                #     value: str = ""

                print(interaction.data, type(interaction.data), sep="\n")
                if interaction.options is not None:
                    # value: str = interaction.data["options"][0]["value"]  # type: ignore
                    value: typing.Optional[str] = interaction.options[0].value
                else:
                    value = None

                if value is None:
                    result = [
                        discord.ApplicationCommandOptionChoice(
                            f"Level {l.level}: {l.name}  -  {l.description}", l.id
                        )
                        for l in locations.locations
                    ]
                else:
                    result = [
                        discord.ApplicationCommandOptionChoice(
                            f"Level {l.level}: {l.name}  -  {l.description}", l.id
                        )
                        for l in locations.locations
                        if value.lower()
                        in "".join(
                            {l.name, l.description, l.id, str(l.emoji), str(l.level)}
                        ).lower()
                    ]
                return await interaction.response.send_autocomplete(result)
        except Exception:
            self.logger.exception("Autocomplete raised exception")  # Fuck you, python.


def setup(bot: vbu.Bot):
    x = BegCommand(bot)
    bot.add_cog(x)


xl: typing.List[typing.Union[int, str]] = [1, 2, 3, "test"]
x = random.choice(xl)
