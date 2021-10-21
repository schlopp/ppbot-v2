import asyncio
import os
import random
import typing

import toml

import discord
from discord.ext import commands, tasks, vbu

from . import utils


class EconomyCommands(vbu.Cog):
    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.bot: vbu.Bot

        self.bot.hyperlink = "https://www.youtube.com/watch?v=FP23VU01fz8"
        if self.bot.is_ready():
            self._load_cache()

    def _load_cache(self):
        """
        Cache some stuff. Only use when bot is loaded.
        """

        # Let's clean up the items cache
        try:
            self.bot.items.clear()
            self.logger.info("Clearing items cache... success")

        # No cache to clean? then we don't need to do anything
        except AttributeError:
            self.logger.warn("Clearing items cache... failed - No items cached")

        if not hasattr(self.bot, "commands_in_use"):
            self.bot.commands_in_use = {}

        # Load each location from ./config/locations
        directory = r"config\items"
        items = []
        for filename in os.listdir(directory):
            if filename.endswith(".toml"):
                items.append(
                    utils.Item.from_dict(
                        self.bot, toml.load(os.path.join(directory, filename))
                    )
                )
        self.bot.items = {
            "shop": {i.id: i for i in items if i.shop_settings.buyable},
            "auction": {i.id: i for i in items if i.shop_settings.auctionable},
            "all": {i.id: i for i in items},
        }
        self.logger.info("Caching items... success")

        # No user cache? Let's create it
        if not hasattr(self.bot, "user_cache"):
            self.bot.user_cache = {}
            self.logger.info("Creating user cache... success")

        # Now let's start the update db from user cache task
        self.update_db_from_user_cache.start()
        self.logger.info("Starting update db from user cache task... success")

        # Now we clean up the begging cache
        try:
            self.bot.begging.clear()
            self.logger.info("Clearing begging cache... success")

        # No cache to clean? then we don't need to do anything
        except AttributeError:
            self.logger.warn(
                "Clearing begging cache... failed - No begging information cached"
            )

        # Create a dictionary for the begging cache
        self.bot.begging = {
            "locations": [],
        }

        # Load each location
        directory = r"config\begging"
        quotes_data = toml.load(os.path.join(directory, "quotes.toml"))
        for filename in os.listdir(os.path.join(directory, "locations")):
            if filename.endswith(".toml"):
                self.bot.begging["locations"].append(
                    utils.BeggingLocation.from_dict(
                        self.bot,
                        toml.load(os.path.join(directory, "locations", filename)),
                        quotes_data,
                    )
                )

        # Load all donators
        self.bot.begging["donators"] = utils.Donators.from_dict(
            toml.load(os.path.join(directory, "donators.toml"))
        )

    @vbu.Cog.listener(name="on_ready")
    async def _load_cache_on_ready(self):
        """
        Cache some stuff when the bot is loaded.
        """

        self._load_cache()

    def cog_unload(self):
        self.update_db_from_user_cache.cancel()

    @tasks.loop(seconds=30.0)
    async def update_db_from_user_cache(self) -> None:
        """
        This task updates the database from the user cache every minute.
        """

        self.logger.info("Updating database from user cache...")

        # Establish a connection to the database
        async with vbu.DatabaseConnection() as db:

            # Iterate through all cached users (convert to list to avoid RuntimeError: dictionary changed size during iteration)
            for user_id, user_cache in list(self.bot.user_cache.items()):

                # Iterate through all of their skills
                skill: utils.Skill
                for skill in user_cache.skills:

                    # Update the user's skill
                    await db(
                        """INSERT INTO user_skill VALUES ($1, $2, $3)
                        ON CONFLICT (user_id, name) DO UPDATE SET
                        experience = user_skill.experience""",
                        user_id,
                        skill.name,
                        skill.experience,
                    )

                    # Log our update
                    self.logger.info(
                        f"Updating user cache for {user_id} - {skill.name!r}... success"
                    )

                # Update the user's pp
                await db(
                    """INSERT INTO user_pp VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id) DO UPDATE SET name = $2,
                    size = $3, multiplier = $4""",
                    user_id,
                    user_cache.pp.name,
                    user_cache.pp.size,
                    user_cache.pp.multiplier,
                )

                # Log our update
                self.logger.info(
                    f"Updating user cache for {user_id}'s pp: {user_cache!r}... success"
                )

                if user_id not in self.bot.commands_in_use:
                    self.bot.user_cache.pop(user_id)

    @commands.command(name="inventory", aliases=["inv"])
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
    async def _inventory_command(self, ctx: commands.SlashContext) -> None:
        """
        View the items in your inventory!
        """

        async with vbu.DatabaseConnection() as db:
            async with utils.Inventory.fetch(self.bot, db, ctx.author.id) as inventory:

                def formatter(menu, items: typing.List[utils.LootableItem]) -> str:
                    with vbu.Embed() as embed:
                        output = []
                        for item in items:
                            output.append(
                                f"2x {item.emoji} **{item.name}** ─ {item.type.replace('_', ' ').title()}"
                                + f"\n **{item.rarity.replace('_', ' ').title()}**"
                                + f"  ─ `{item.id}` {item.description}"
                            )
                        embed.set_author(
                            name=f"{ctx.author.display_name}'s inventory",
                            icon_url=ctx.author.avatar.url,
                        )
                        embed.description = (
                            f"use [/item-info [item]]({self.bot.hyperlink}) for more information.\n\n"
                            + "\n\n".join(output)
                        )
                        embed.set_footer(
                            f"Page {menu.current_page + 1}/{menu.max_pages}"
                        )
                    return embed

                sorters = utils.Sorters(
                    "ALPHABETICAL",
                    utils.Sorter(
                        "name (A ➞ Z)",
                        "Sort items alphabetically",
                        "ALPHABETICAL",
                        lambda i: sorted(i, key=lambda x: x.name),
                    ),
                    utils.Sorter(
                        "name (Z ➞ A)",
                        "Sort items reverse-alphabetically",
                        "REVERSE_ALPHABETICAL",
                        lambda i: sorted(i, key=lambda x: x.name, reverse=True),
                    ),
                    utils.Sorter(
                        "rarity (GODLIKE ➞ COMMON)",
                        "Sort items based on their rarity from highest to lowest",
                        "RARITY",
                        lambda i: sorted(
                            i,
                            key=lambda x: {
                                "ADMIN-ABUSE": 0,
                                "GODLIKE": 1,
                                "LEGENDARY": 2,
                                "RARE": 3,
                                "UNCOMMON": 4,
                                "COMMON": 5,
                            }[x.rarity],
                        ),
                    ),
                    utils.Sorter(
                        "rarity (COMMON ➞ GODLIKE)",
                        "Sort items based on their rarity from lowest to highest",
                        "REVERSE_RARITY",
                        lambda i: sorted(
                            i,
                            key=lambda x: {
                                "COMMON": 0,
                                "UNCOMMON": 1,
                                "RARE": 2,
                                "LEGENDARY": 3,
                                "GODLIKE": 4,
                                "ADMIN-ABUSE": 5,
                            }[x.rarity],
                        ),
                    ),
                )

                filters = utils.Filters(
                    utils.Filter(
                        "Crafting reagents",
                        "CREATING_REAGENT",
                        filterer=lambda i: list(
                            filter(lambda x: x.type == "CRAFTING_REAGENT", i)
                        ),
                    ),
                    utils.Filter(
                        "Tools",
                        "TOOL",
                        filterer=lambda i: list(filter(lambda x: x.type == "TOOL", i)),
                    ),
                    utils.Filter(
                        "Potions",
                        "POTION",
                        filterer=lambda i: list(
                            filter(lambda x: x.type == "POTION", i)
                        ),
                    ),
                )

                paginator = utils.Paginator(
                    inventory.items,
                    per_page=5,
                    formatter=formatter,
                    sorters=sorters,
                    filters=filters,
                )
                await paginator.start(ctx, timeout=10)

    @commands.command(name="show")
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
    async def _show_pp(self, ctx: commands.SlashContext) -> None:
        async with vbu.DatabaseConnection() as db:
            cache: utils.CachedUser = await utils.get_user_cache(
                ctx.author.id,
                db=db,
                bot=self.bot,
                logger=self.logger,
            )
            with vbu.Embed() as embed:
                embed.colour = utils.BLUE
                embed.set_author(
                    name=f"{ctx.author.display_name}'s PP",
                    icon_url=ctx.author.avatar.url,
                )
                embed.description = f"8{('='*(cache.pp.size // 50))[:1000]}D"
                embed.add_field(
                    "Stats",
                    f"Size - {cache.pp.size}\nMultiplier - {cache.pp.multiplier}",
                )
            await ctx.interaction.response.send_message(embed=embed)

    @commands.command(name="beg")
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
    async def _beg_command(self, ctx: commands.SlashContext) -> None:
        """
        Beg for inches, earn items, and get a large pp in the process!
        """

        with utils.UsingCommand(ctx):
            async with vbu.DatabaseConnection() as db:

                cache: utils.CachedUser = await utils.get_user_cache(
                    ctx.author.id,
                    db=db,
                    bot=self.bot,
                    logger=self.logger,
                )
                begging = cache.get_skill("BEGGING")

                locations = utils.BeggingLocations(
                    begging.level, *self.bot.begging["locations"]
                )

                components = discord.ui.MessageComponents(
                    discord.ui.ActionRow(locations.to_select_menu())
                )
                content = "\n".join(
                    (
                        f"**Where are you begging?**",
                        f"Level up `BEGGING` unlock new locations!",
                        f"**Current level:** {utils.int_to_roman(begging.level)}",
                    )
                )

                await ctx.interaction.response.send_message(
                    content, components=components
                )

                try:
                    original_message = await ctx.interaction.original_message()

                    def check(
                        interaction: discord.Interaction,
                    ) -> typing.Union[bool, None]:
                        # Check if the interaction is used the original context interaction message.
                        if interaction.message.id != original_message.id:
                            return
                        if interaction.user != ctx.author:
                            self.bot.loop.create_task(
                                interaction.response.send_message(
                                    content="Bro this is not meant for you LMAO",
                                    ephemeral=True,
                                )
                            )
                            return
                        return True

                    # Wait for a response
                    payload: discord.Interaction = await self.bot.wait_for(
                        "component_interaction",
                        check=check,
                        timeout=15.0,
                    )
                except asyncio.TimeoutError:
                    return await ctx.interaction.edit_original_message(
                        content=content
                        + "\n\n\\🟥 You took WAY too long to respond `waited 15.0s`",
                        components=components.disable_components(),
                    )

                # Get the selected location
                location: utils.BeggingLocation = (
                    locations.get_location_from_interaction(payload)
                )
                if locations is None:
                    raise Exception("Invalid location")

                # 5% chance of fill in the blank minigame
                if (random_percentage := random.random()) < 0.05:
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
                                    "Whoever threw that paper, your mom's a `[ _ _ _ ]`!",
                                    "HOE",
                                ),
                                (
                                    "I have the power of `[ _ _ _   _ _ _   _ _ _ _ _ ]` on my side!",
                                    "GOD AND ANIME",
                                ),
                                (
                                    "*dodges bullets like in The `[ _ _ _ _ _ _ ]`*",
                                    "MATRIX",
                                ),
                                ("You'll never `[ _ _ _ _ ]` me alive! *doot*", "TAKE"),
                                ("Doin' your [ _ _ _ ]", "MOM"),
                                (
                                    "Shut yo skin tone [ _ _ _ _ _ _ _ ] bone google chrome no home flip phone disowned ice cream cone garden gnome extra chromosome metronome dimmadome head ass tf up",
                                    "CHICKEN",
                                ),
                            ]
                        )

                        embed.description = f"{fill_in_the_blank.context}\n\n**{fill_in_the_blank.approacher}:** “{prompt}”"
                        embed.set_footer("Respond to this message with the answer")
                    await ctx.interaction.edit_original_message(
                        embed=embed, components=None, content=None
                    )

                    try:
                        answer_message = await self.bot.wait_for(
                            "message",
                            check=lambda m: m.author == ctx.author
                            and m.content.upper() == answer,
                            timeout=15.0,
                        )
                    except asyncio.TimeoutError:
                        with embed:
                            embed.description = f"bruh, the answer was {answer}, but you took WAY too long to respond. You get {utils.format_rewards()}.\n\n**{fill_in_the_blank.approacher}:** {fill_in_the_blank.fail}"
                        return await ctx.interaction.edit_original_message(embed=embed)

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

                        # Get a random quote and format it with the reward
                        quote = fill_in_the_blank.success.format(
                            utils.format_rewards(inches=growth, items=loot)
                        )

                        # Set the embed's description to the quote
                        embed.description = (
                            f"**{fill_in_the_blank.approacher}:** “{quote}”"
                        )

                    # Update the message
                    return await ctx.interaction.edit_original_message(
                        embed=embed, components=None, content=None
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

                    await ctx.interaction.edit_original_message(
                        embed=embed, components=None, content=None
                    )

                    attempts_left = 3

                    def scramble_check(message: discord.Message) -> bool:

                        if (
                            message.author != ctx.author
                            or message.channel != ctx.channel
                        ):
                            return

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
                            return

                        return True

                    while attempts_left:
                        try:
                            answer_message = await self.bot.wait_for(
                                "message",
                                check=scramble_check,
                                timeout=15.0,
                            )
                            break
                        except asyncio.TimeoutError:
                            with embed:
                                embed.description = f"You should work on your scrambling skills, the answer was `{unscrambled}`. You get {utils.format_rewards()}"
                            return await ctx.interaction.edit_original_message(
                                embed=embed
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
                    return await ctx.interaction.edit_original_message(
                        embed=embed, components=None, content=None
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

                        sentence = random.choice(retype.sentences)
                        uncopyable_sentence = utils.uncopyable(sentence)

                        embed.description = f"{fill_in_the_blank.context}\n\nQuickly! Retype this sentence is chat: [`{uncopyable_sentence}`]({self.bot.hyperlink})"
                        embed.set_footer("Respond to this message with the sentence")

                    await ctx.interaction.edit_original_message(
                        embed=embed, components=None, content=None
                    )

                    attempts_left = 3

                    def retype_check(message: discord.Message) -> bool:

                        if (
                            message.author != ctx.author
                            or message.channel != ctx.channel
                        ):
                            return

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
                            return

                        return True

                    while attempts_left:
                        try:
                            answer_message = await self.bot.wait_for(
                                "message",
                                check=scramble_check,
                                timeout=30.0,
                            )
                            break
                        except asyncio.TimeoutError:
                            embed.description = f"Wow, you're a slow typer. You get {utils.format_rewards()}. Cry about it"
                            return await ctx.interaction.edit_original_message(
                                embed=embed
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
                    return await ctx.interaction.edit_original_message(
                        embed=embed, components=None, content=None
                    )

                else:
                    # Update database and build the embed for receiving a generic donation.
                    with vbu.Embed() as embed:
                        embed.colour = utils.BLUE
                        donators: utils.Donators = self.bot.begging["donators"]
                        donator = donators.get_random_donator()

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
                    await ctx.interaction.edit_original_message(
                        embed=embed, components=None, content=None
                    )


def setup(bot: vbu.Bot):
    x = EconomyCommands(bot)
    bot.add_cog(x)
