import typing
import asyncio
import inspect
import itertools

import discord
from discord.ext import commands, vbu


__all__ = (
    "Filter",
    "Filters",
    "Sorter",
    "Sorters",
    "Paginator",
)


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

    def __init__(self, *options: typing.Iterable[Filter]):
        self.current_filters: typing.List[Filter] = []
        options = list(options)
        self.options = {f.id: f for f in options}

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

    def filter(self, data: typing.Sequence):
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
        *options: typing.Iterable[Sorter],
    ):
        """
        Args:
            default (optional :class:`Union` of :class:`Sorter` and `str`): The default `Sorter`.
                If no other method is specified by the user, this method will be used.
                If this is of type `str`, it must be the ID of a `Sorter` in `options`.
                Will default to the first `Sorter` in `options`.
            options (:class:`Iterable` of :class:`Sorter`): A list of `Sorter`s to use.
                Must atleast contain atleast one `Sorter` if `default` is not specified to a :class:`Sorter`.
        """

        options = list(options)
        if not isinstance(default, (Sorter, str, None)):
            raise TypeError("`default` must be of type `Sorter`, `str` or `None`")
        elif default is None:
            try:
                self.default = options[0]
            except IndexError:
                raise ValueError("No default sorter specified and no sorters available")
        elif isinstance(default, str):
            try:
                self.default = next(s for s in options if s.id == default)
            except StopIteration:
                self.default = None
            if self.default is None:
                raise ValueError(f"No default sorter with ID `{self.default}` found")
            options.pop(options.index(self.default))
        else:
            self.default = default
        self.default: Sorter
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

    def __init__(
        self,
        data: typing.Union[
            typing.Sequence, typing.Generator, typing.Callable[[int], typing.Any]
        ],
        *,
        per_page: typing.Optional[int] = 10,
        formatter: typing.Optional[
            typing.Callable[
                ["Paginator", typing.Sequence[typing.Any]],
                typing.Union[str, discord.Embed, dict],
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
                function taking the paginator instance and a list of things to display, returning a dictionary of kwargs that get passed
                directly into a :func:`discord.Message.edit`.
        """
        if not isinstance(data, typing.Sequence):
            self.sorters = None
            self.filters = None
            self.data = data
            self.filtered_data = self.data
        else:
            data = list(data)
            self.sorters: Sorters = sorters
            if self.sorters.current_sorter is not None:
                self.data = data
                self.filtered_data = self.sorters.current_sorter.sorter(data)
            else:
                self.data = data
                self.filtered_data = self.data
            self.filters: Filters = filters
        self.per_page: int = per_page
        self.formatter: typing.Callable[
            ["Paginator", typing.Sequence[typing.Any]],
            typing.Union[str, discord.Embed, dict],
        ]
        if formatter is None:
            self.formatter = self.default_list_formatter
        else:
            self.formatter = formatter
        self.current_page: int = None
        self._page_cache = {}

        self.max_pages: int = "?"
        self._data_is_generator = any(
            (
                inspect.isasyncgenfunction(self.data),
                inspect.isasyncgen(self.data),
                inspect.isgeneratorfunction(self.data),
                inspect.isgenerator(self.data),
            )
        )
        self._data_is_function = any(
            (
                inspect.isfunction(self.data),
                inspect.iscoroutine(self.data),
            )
        )
        self._data_is_iterable = not (self._data_is_generator or self._data_is_function)
        if self._data_is_iterable:
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
                    ctx, content="There's literally nothing here LMAO"
                )
                break

            # Format the page data
            payload: typing.Dict[str, typing.Any] = self.formatter(self, items)
            if isinstance(payload, discord.Embed):
                payload = {"embeds": [payload]}
            elif isinstance(payload, str):
                payload = {"content": payload}
            if embed := payload.pop("embed", None):
                payload.update({"embeds": [embed]})

            # Set a default for these things
            payload.setdefault("content", None)
            payload.setdefault("embeds", None)

            # Work out what components to show
            components = self.get_pagination_components()

            # See if the content is unchanged
            if payload != last_payload:
                await self._edit_message(ctx, **payload, components=components)

            # See if we want to bother paginating
            last_payload = payload
            if self.max_pages == 1 and not self.filters.current_filters:
                break

            # Wait for reactions to be added by the user
            interaction = None
            try:
                check = (
                    lambda p: p.user.id == ctx.author.id
                    and p.message.id == self._message.id
                )
                interaction: discord.Interaction = await ctx.bot.wait_for(
                    "component_interaction", check=check, timeout=timeout
                )
                await interaction.response.defer_update()
            except asyncio.TimeoutError:
                break

            # Change the item order based on the component interaction
            if interaction.component.custom_id == "SORTER":
                self.current_page = 0
                if self.sorters is not None:
                    self.sorters.current_sorter = self.sorters.options[
                        interaction.data["values"][0]
                    ]

                    # Clear the cache
                    self._page_cache.clear()

            elif interaction.component.custom_id == "FILTER":
                self.current_page = 0
                if self.filters is not None:
                    self.filters.current_filters = [
                        self.filters.options[v] for v in interaction.data["values"]
                    ]

                    # Clear the cache
                    self._page_cache.clear()

            else:
                # Change the page number based on the component interaction
                self.current_page = {
                    "START": lambda i: 0,
                    "PREVIOUS": lambda i: i - 1,
                    "NEXT": lambda i: i + 1,
                    "END": lambda i: self.max_pages,
                }[str(interaction.component.custom_id)](self.current_page)

                # Make sure the page number is still valid
                if self.max_pages != "?" and self.current_page >= self.max_pages:
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
                    disabled=self.max_pages != "?"
                    and self.current_page >= self.max_pages - 1,
                ),
                discord.ui.Button(
                    emoji="<:END:892833141205647430>",
                    custom_id="END",
                    disabled=self.max_pages == "?"
                    or self.current_page >= self.max_pages - 1,
                ),
            ),
        )
        if self.sorters is not None:
            components.add_component(
                discord.ui.ActionRow(self.sorters.to_selectmenu()),
            )
        if self.filters is not None:
            components.add_component(
                discord.ui.ActionRow(self.filters.to_selectmenu()),
            )
        return components

    async def get_page(self, page_number: int) -> typing.List[typing.Any]:
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
            pass
        try:
            if self.sorters is None:
                if inspect.isasyncgenfunction(self.data) or inspect.isasyncgen(
                    self.data
                ):
                    v = await self.data.__anext__()
                elif inspect.isgeneratorfunction(self.data) or inspect.isgenerator(
                    self.data
                ):
                    v = next(self.data)
                elif inspect.iscoroutinefunction(self.data):
                    v = await self.data(page_number)
                elif inspect.isfunction(self.data):
                    v = self.data(page_number)
                else:
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
        except (StopIteration, StopAsyncIteration):
            self.max_pages = page_number
            page_number -= 1
            self.current_page -= 1
        if self._data_is_iterable:
            pages, left_over = divmod(len(self.filtered_data), self.per_page)
            if left_over:
                pages += 1
            self.max_pages = pages
        return self._page_cache[page_number]

    @staticmethod
    def default_list_formatter(
        m: "Paginator", d: typing.List[typing.Union[str, discord.Embed]]
    ):
        """
        The default list formatter for embeds. Takes the paginator instance and the list of data
        to be displayed, and returns a dictionary of kwargs for a `Message.edit`.
        """

        if isinstance(d[0], discord.Embed):
            return {"embeds": d}
        return vbu.Embed(use_random_colour=True, description="\n".join(d),).set_footer(
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
