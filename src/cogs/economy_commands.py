import os
import typing

import toml
import discord  # type: ignore
from discord.ext import commands, tasks, vbu  # type: ignore

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

    @commands.command(name="inventory", add_slash_command=True)
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

                def formatter(
                    menu: utils.Paginator, items: typing.List[utils.LootableItem]
                ) -> vbu.Embed:
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

    @commands.command(name="show", add_slash_command=True)
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


def setup(bot: vbu.Bot):
    x = EconomyCommands(bot)
    bot.add_cog(x)
