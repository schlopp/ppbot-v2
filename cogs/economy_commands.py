import random
import asyncio
import os
import textwrap
import typing

import toml

import discord
from discord.ext import commands, tasks, vbu

from . import utils


class EconomyCommands(vbu.Cog):
    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.bot: vbu.Bot

        self.hyperlink = "https://www.youtube.com/watch?v=FP23VU01fz8"
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

        # Load each location from ./config/begging/locations
        directory = r"config\begging\locations"
        for filename in os.listdir(directory):
            if filename.endswith(".toml"):
                self.bot.begging["locations"].append(
                    utils.BeggingLocation.from_dict(
                        self.bot, toml.load(os.path.join(directory, filename))
                    )
                )

        # Load all donators from ./config/begging/donators.toml
        directory = r"config\begging\donators.toml"
        self.bot.begging["donators"] = utils.begging.Donators.from_dict(
            toml.load(directory)
        )

    @vbu.Cog.listener(name="on_ready")
    async def _load_cache_on_ready(self):
        """
        Cache some stuff when the bot is loaded.
        """

        self._load_cache()

    def cog_unload(self):
        self.update_db_from_user_cache.cancel()

    async def get_user_cache(
        self, user_id: int, db: typing.Optional[vbu.DatabaseConnection]
    ) -> utils.CachedUser:
        """
        Returns user's cached information, if any. Otherwise returns data from the database.

        Args:
            user_id (`int`): The user's ID.
            db (:class:`voxelbotutils.DatabaseConnection`): The database connection.

        Returns:
            `dict`: The user's cache.
        """

        # If the user is already cached, return it
        try:
            return self.bot.user_cache[user_id]

        # Otherwise, let's create it
        except KeyError:

            # Get the user's skills
            user_skill_rows = await db(
                "SELECT * FROM user_skill WHERE user_id = $1", user_id
            )
            user_skills = [utils.Skill(**i) for i in user_skill_rows]

            # Now let's get the user's pp
            try:
                pp_rows = await db("SELECT * FROM user_pp WHERE user_id = $1", user_id)
                user_pp = utils.Pp(**pp_rows[0])

            # apparently the user doesn't have pp? Let's create one
            except IndexError:
                user_pp = utils.Pp(user_id)

            # Now we add this to the user cache
            self.bot.user_cache[user_id] = utils.CachedUser(
                user_id, user_skills, user_pp
            )

            # we do a little logging. it's called: "We do a little logging"
            self.logger.info(f"Creating user cache for {user_id}... success")

            # and return the user cache
            return self.bot.user_cache[user_id]

    @tasks.loop(seconds=30.0)
    async def update_db_from_user_cache(self) -> None:
        """
        This task updates the database from the user cache every minute.
        """

        self.logger.info("Updating database from user cache...")

        # Establish a connection to the database
        async with vbu.DatabaseConnection() as db:

            # Iterate through all cached users
            for user_id, user_cache in self.bot.user_cache.items():

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

        self.bot.user_cache.clear()

    @commands.command(name="inventory", aliases=["inv"])
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
    async def _inventory_command(self, ctx: commands.SlashContext) -> None:
        """
        View the items in your inventory!
        """

        async with vbu.DatabaseConnection() as db:
            async with utils.Inventory.fetch(self.bot, db, ctx.author.id) as inventory:

                def formatter(menu, items: typing.List[utils.LootableItem]) -> str:
                    output = []
                    for item in items:
                        output.append(
                            f"{item.amount}x {item.name} ─ **{item.rarity}**"
                            + f"\n`{item.id}` {item.description}"
                        )

                    with vbu.Embed() as embed:
                        embed.set_author(
                            name=f"{ctx.author.display_name}'s inventory",
                            icon_url=ctx.author.avatar_url,
                        )
                        embed.description = (
                            f"use [/item-info [ITEM_ID]]({self.hyperlink}) for more information.\n\n"
                            + "\n\n".join(output)
                        )
                    return embed

                paginator = utils.Paginator(
                    inventory.items, per_page=5, formatter=formatter
                )
                await paginator.start(ctx)

    @commands.command(name="beg")
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
    async def _beg_command(self, ctx: commands.SlashContext) -> None:
        """
        Beg for inches, earn items, and get a large pp in the process!
        """

        async with vbu.DatabaseConnection() as db:

            # Get the user's cache
            cache: utils.CachedUser = await self.get_user_cache(ctx.author.id, db)
            begging = cache.get_skill("BEGGING")

            # Set up the begging locations with the user's current begging level
            locations = utils.begging.BeggingLocations(
                begging.level, *self.bot.begging["locations"]
            )

            # Build the message
            components = discord.ui.MessageComponents(
                discord.ui.ActionRow(locations.to_select_menu())
            )
            content = textwrap.dedent(
                f"""
                <:thonk:881578428506185779> **Where are you begging?**
                Level up `BEGGING` unlock new locations!
                **Current level:** {utils.readable.int_formatting.int_to_roman(begging.level)}
            """
            )

            # Send the message
            message: discord.InteractionMessage = await ctx.interaction.original_message.send_message(
                content, components=components
            )

            try:
                # Wait for a response
                payload: discord.Interaction = await self.bot.wait_for(
                    "component_interaction",
                    check=lambda p: p.message.id == message.id
                    and p.user.id == ctx.author.id,
                    timeout=60.0,
                )
            except asyncio.TimeoutError:
                components.disable_components()
                content = (
                    content + "\n\\🟥 **You took too long to respond** 😔 `waited 60.0s`"
                )
                return await message.edit(content=content, components=components)

            # Get the selected location
            location = locations.get_location_from_interaction(payload)

            # 5% chance of fill in the blank minigame
            if (random_percentage := random.random()) < 0.05:
                raise NotImplementedError(
                    "The 'fill in the blank' minigame has not been added yet."
                )

            # Update database and build the embed for receiving a generic donation.
            with vbu.Embed(use_random_colour=True) as embed:
                donators: utils.begging.Donators = self.bot.begging["donators"]
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
                    utils.readable.rewards.format_rewards(inches=growth, items=loot)
                )

                # Set the embed's author
                embed.set_author(
                    name=f"{donator.name} \N{bullet} {location.name}",
                    icon_url=donator.icon_url,
                )

                # Set the embed's description to the quote
                embed.description = f"“{quote}”"

            # Update the message
            await payload.update_message(embed=embed, components=None, content=None)


def setup(bot: vbu.Bot):
    x = EconomyCommands(bot)
    bot.add_cog(x)
