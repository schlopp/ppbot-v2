import asyncio
import inspect
import itertools
import typing

import discord  # type: ignore
from discord.ext import commands, vbu  # type: ignore
from discord.interactions import Interaction  # type: ignore

__all__ = (
    "Filter",
    "Filters",
    "Sorter",
    "Sorters",
    "Paginator",
)


class _EmbedsDict(typing.TypedDict):
    embeds: typing.List[discord.Embed]


class _PayloadDict(typing.TypedDict):
    embeds: typing.Optional[typing.List[discord.Embed]]
    content: typing.Optional[str]


_EmbedOrStringList = typing.List[typing.Union[discord.Embed, str]]


class Filter:
    """
    A filter method to use within the class :class:`Sorters`.
    """

    def __init__(
        self,
        label: str,
        id: str,
        *,
        description: typing.Optional[str] = None,
        filterer: typing.Callable[[list], list],
    ):
        self.label = label
        self.id = id
        self.description = description
        self.filterer = filterer


class Filters:
    """
    A container of filter methods to use within the :class:`Paginator`

    Args:
        options (`dict`) A dictionary of :class:`Filter`s to use.
        current_filter  (:class:`Filter`): The current :class:`Filter` in usage.
    """

    def __init__(self, *options: Filter):
        self.current_filters: typing.List[Filter] = []
        self.options: typing.Dict[str, Filter] = {f.id: f for f in options}

    def to_selectmenu(self):
        """
        Get a :class:`discord.ui.SelectMenu` based on the sorters.
        """

        return discord.ui.SelectMenu(
            custom_id="FILTER",
            placeholder="Filter...",
            min_values=0,
            max_values=len(self.options) - 1 if len(self.options) > 1 else 1,
            options=[
                discord.ui.SelectOption(
                    label=s.label,
                    value=s.id,
                    description=s.description,
                    default=s in self.current_filters,
                )
                for s in self.options.values()
            ],
        )

    def filter(self, data: typing.List):
        """
        Filter the data based on the current filters.
        """

        if not self.current_filters:
            return data
        filtered = []
        for i in self.current_filters:
            filtered.append(i.filterer(data))
        x = list(
            filtered
            for filtered, _ in itertools.groupby(
                sorted([j for i in filtered for j in i], key=lambda x: x.id)
            )
        )
        return x


class Sorter:
    """
    A container of sorting methods to use with in the :class:`Paginator`

    Args:
        options (`dict`): A dictionary of `Sorter`s to use.
        current_sorter (:class:`Sorter`): The current :class:`Sorter` in usage.
    """

    def __init__(
        self,
        label: str,
        description: str,
        id: str,
        sorter: typing.Callable[[list], list],
    ):
        self.label = label
        self.description = description
        self.id = id
        self.sorter = sorter


class Sorters:
    """
    A container of sorting methods to use within the :class:`Paginator`

    Args:
        default (`str`): The default `Sorter`.
        options (:class: `dict`): A dictionary of `Sorter`s to use.
        current_sorter (:class:`Sorter`): The current `Sorter` in usage.
    """

    def __init__(
        self,
        default: typing.Optional[typing.Union[Sorter, str]] = None,
        *options: Sorter,
    ):
        """
        Args:
            default (optional :class:`Union` of :class:`Sorter` and `str`): The default `Sorter`.
                If no other method is specified by the user, this method will be used.
                If this is of type `str`, it must be the ID of a `Sorter` in `options`.
                Will default to the first `Sorter` in `options`.
            options (:class:`Sorter`): A list of `Sorter`s to use.
                Must atleast contain atleast one `Sorter` if `default` is not specified to a :class:`Sorter`.
        """

        # Need the options to be mutable
        options_list = list(options)
        if default is None:
            try:
                self.default: typing.Optional[Sorter] = options_list[0]
            except IndexError:
                raise ValueError("No default sorter specified and no sorters available")
        elif isinstance(default, str):
            try:
                self.default = next(s for s in options_list if s.id == default)
            except StopIteration:
                self.default = None
            if self.default is None:
                raise ValueError(f"No default sorter with ID `{self.default}` found")
            options_list.pop(options_list.index(self.default))
        else:
            self.default = default
        self.options = {self.default.id: self.default, **{s.id: s for s in options}}
        self.current_sorter = self.default

    def to_selectmenu(self):
        """
        Get a :class:`discord.ui.SelectMenu` based on the sorters.
        """

        return discord.ui.SelectMenu(
            custom_id="SORTER",
            options=[
                discord.ui.SelectOption(
                    label=s.label,
                    value=s.id,
                    description=s.description,
                    default=s == self.current_sorter,
                )
                for s in self.options.values()
            ],
        )


class Paginator:
    """
    An automatic paginator util that takes a list and listens for reactions on a message
    to change the content.
    ::
        # Items will automatically be cast to strings and joined
        my_list = list(range(30))
        p = utils.Paginator(my_list, per_page=5)
        await p.start(ctx, timeout=15)
        # Alternatively you can give a function, which can return a string, an embed, or a dict
        # that gets unpacked directly into the message's edit method
        def my_formatter(menu, items):
            output = []
            for i in items:
                output.append(f"The {i}th item")
            output_string = "\\n".join(output)
            embed = discord.Embed(description=output_string)
            embed.set_footer(f"Page {menu.current_page + 1}/{menu.max_pages}")
        p = utils.Paginator(my_list, formatter=my_formatter)
        await p.start(ctx)
    """

    sorters: typing.Optional[Sorters]

    def __init__(
        self,
        data: typing.Sequence,
        *,
        per_page: int = 10,
        formatter: typing.Optional[
            typing.Callable[
                ["Paginator", list],
                typing.Union[str, discord.Embed, _EmbedsDict],
            ]
        ] = None,
        sorters: typing.Optional[Sorters] = None,
        filters: typing.Optional[Filters] = None,
    ):
        """
        Args:
            data (typing.Union[typing.Sequence, typing.Generator, typing.Callable[[int], typing.Any]]): The
                data that you want to paginate.
                If a generator or function is given then the `max_pages` will start as the string "?", and the `per_page`
                parameter will be ignored - the formatter will be passed the content of whatever your generator returns.
                If a function is given, then you will be passed the page number as an argument - raising
                `StopIteration` from this function will cause the `max_pages` attribute to be set,
                and the page will go back to what it was previously.
            per_page (int, optional): The number of items that appear on each page. This argument only works for sequences
            formatter (typing.Callable[['Paginator', typing.Sequence[typing.Any]], typing.Union[str, discord.Embed, dict]], optional): A
                function takinRg the paginator instance and a list of things to display, returning a dictionary of kwargs that get passed
                directly into a :func:`discord.Message.edit`.
        """

        self.data = list(data)
        self.sorters = sorters
        if self.sorters is not None and self.sorters.current_sorter is not None:
            self.filtered_data = self.sorters.current_sorter.sorter(self.data)
        else:
            self.filtered_data = self.data
        self.filters: typing.Optional[Filters] = filters
        self.per_page: int = per_page
        self.formatter = self.default_list_formatter if formatter is None else formatter
        self._page_cache: typing.Dict[int, list] = {}

        self.current_page = 0
        pages, left_over = divmod(len(data), self.per_page)
        if left_over:
            pages += 1
        self.max_pages = pages
        self._message = None

    async def _edit_message(self, ctx, *args, **kwargs):
        if self._message is None:
            self._message = await ctx.send(*args, **kwargs)
        else:
            try:
                await self._message.edit(*args, **kwargs)
            except discord.errors.NotFound:
                pass

    async def start(self, ctx: commands.Context, *, timeout: float = 120):
        """
        Start and handle a paginator instance.
        Args:
            ctx (discord.ext.commands.Context): The context instance for the called command.
            timeout (float, optional): How long you should wait between getting a reaction
                and timing out.
        """

        # Set our initial values
        self.current_page = 0
        if self.max_pages == 0:
            await ctx.send("There's literally nothing here LMAO")
            return

        # Set up our initial components as to not get hit with an UnboundLocalError
        components = self.get_pagination_components()

        # Loop the reaction handler
        last_payload = None
        while True:

            # Get the page data
            try:
                items = await self.get_page(self.current_page)
            except (KeyError, IndexError):
                await self._edit_message(
                    ctx, content="There's literally nothing on this page lol"
                )
                break

            # Format the page data
            formatter_payload = self.formatter(self, items)
            payload: _PayloadDict = {"content": None, "embeds": None}
            if isinstance(formatter_payload, discord.Embed):
                payload["embeds"] = [formatter_payload]
            elif isinstance(formatter_payload, str):
                payload["content"] = formatter_payload
            else:
                payload["embeds"] = formatter_payload["embeds"]

            # Work out what components to show
            components = self.get_pagination_components()

            # See if the content is unchanged
            if payload != last_payload:
                await self._edit_message(ctx, **payload, components=components)

            # See if we want to bother paginating
            last_payload = payload
            if self.max_pages == 1 and (
                (not self.filters) or not self.filters.current_filters
            ):
                break

            # Wait for reactions to be added by the user
            try:
                check: typing.Callable[[discord.Interaction], typing.Any] = (
                    lambda p: p.user.id == ctx.author.id  # type: ignore
                    and p.message.id == self._message.id  # type: ignore
                )

                interaction: discord.Interaction = await ctx.bot.wait_for(
                    "component_interaction", check=check, timeout=timeout
                )
                await interaction.response.defer_update()
            except asyncio.TimeoutError:
                break

            # Change the item order based on the component interaction
            assert interaction.component is not None
            if interaction.component.custom_id == "SORTER":
                self.current_page = 0
                if self.sorters is not None:
                    assert interaction.data is not None
                    self.sorters.current_sorter = self.sorters.options[
                        interaction.data["values"][0]
                    ]

                    # Clear the cache
                    self._page_cache.clear()

            elif interaction.component.custom_id == "FILTER":
                self.current_page = 0
                if self.filters is not None:
                    assert interaction.data is not None
                    self.filters.current_filters = [
                        self.filters.options[v] for v in interaction.data["values"]
                    ]

                    # Clear the cache
                    self._page_cache.clear()

            else:
                # Change the page number based on the component interaction
                find_page: typing.Dict[str, typing.Callable[[int], int]] = {
                    "START": lambda i: 0,
                    "PREVIOUS": lambda i: i - 1,
                    "NEXT": lambda i: i + 1,
                    "END": lambda i: self.max_pages,
                }
                self.current_page = find_page[str(interaction.component.custom_id)](
                    self.current_page
                )

                # Make sure the page number is still valid
                if self.current_page >= self.max_pages:
                    self.current_page = self.max_pages - 1
                elif self.current_page < 0:
                    self.current_page = 0

        # Let us break from the loop
        ctx.bot.loop.create_task(
            self._edit_message(ctx, components=components.disable_components())
        )

    def get_pagination_components(self):
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    emoji="<:START:892833211120496721>",
                    custom_id="START",
                    disabled=self.current_page == 0,
                ),
                discord.ui.Button(
                    emoji="<:PREVIOUS:892833166950273075>",
                    custom_id="PREVIOUS",
                    disabled=self.current_page == 0,
                ),
                discord.ui.Button(
                    emoji="<:NEXT:892832013491503124>",
                    custom_id="NEXT",
                    disabled=self.current_page >= self.max_pages - 1,
                ),
                discord.ui.Button(
                    emoji="<:END:892833141205647430>",
                    custom_id="END",
                    disabled=self.current_page >= self.max_pages - 1,
                ),
            ),
        )

        if any(self.sorters is not None, self.filters is not None):
            select_action_row = discord.ui.ActionRow()
            if self.sorters is not None:
                select_action_row.add_component(self.sorters.to_selectmenu())
            if self.filters is not None:
                select_action_row.add_component(self.filters.to_selectmenu())
            components.add_component(select_action_row)
        return components

    async def get_page(self, page_number: int) -> list:
        """
        Get a list of items that appear for a given page.
        Args:
            page_number (int): The page number to get.
        Returns:
            typing.List[typing.Any]: The list of items that would be on the page.
        """

        try:
            return self._page_cache[page_number]
        except KeyError:
            if self.sorters is None:
                v = self.data[
                    page_number * self.per_page : (page_number + 1) * self.per_page
                ]
                self._page_cache[page_number] = v
            else:
                if (
                    self.filters is not None
                    and self.filters.current_filters is not None
                ):
                    self.filtered_data = self.filters.filter(self.data)
                self.filtered_data = self.sorters.current_sorter.sorter(
                    self.filtered_data
                )
                v = self.filtered_data[
                    page_number * self.per_page : (page_number + 1) * self.per_page
                ]
                self._page_cache[page_number] = v
            return self._page_cache[page_number]

    @staticmethod
    def default_list_formatter(
        m: "Paginator", d: _EmbedOrStringList
    ) -> typing.Union[_EmbedsDict, discord.Embed]:
        """
        The default list formatter for embeds. Takes the paginator instance and the list of data
        to be displayed, and returns a dictionary of kwargs for a `Message.edit`.
        """

        if all(isinstance(i, discord.Embed) for i in d):
            if typing.TYPE_CHECKING:
                typed_embeds_d = typing.cast(_EmbedsDict, {"embeds": d})
            else:
                typed_embeds_d = {"embeds": d}
            return typed_embeds_d
        else:
            if typing.TYPE_CHECKING:
                typed_str_d = typing.cast(typing.List[str], d)
            else:
                typed_str_d = d
            return vbu.Embed(
                use_random_colour=True,
                description="\n".join(typed_str_d),
            ).set_footer(
                f"Page {m.current_page + 1}/{m.max_pages}",
            )

    @staticmethod
    def default_ranked_list_formatter(m: "Paginator", d: typing.List[str]):
        """
        The default list formatter for embeds. Takes the paginator instance and the list of strings to be displayed,
        and returns a dictionary of kwargs for a `Message.edit`.
        """

        return vbu.Embed(
            use_random_colour=True,
            description="\n".join(
                [
                    f"{i}. {o}"
                    for i, o in enumerate(d, start=(m.current_page * m.per_page) + 1)
                ]
            ),
        ).set_footer(
            f"Page {m.current_page + 1}/{m.max_pages}",
        )
