import typing
import random

import voxelbotutils as vbu
from discord.ext import tasks

from cogs import utils


class Shop(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.items: typing.List[utils.Item] = []
        self.load_items.start()
        self.item_not_exist = 'cmonbruh that item doesn\'t exist what are you DOING'

    @tasks.loop(hours=1)
    async def load_items(self):
        async with vbu.DatabaseConnection() as db:
            self.items = await utils.fetch_items(db, for_sale=True)

    def cog_unload(self):
        self.load_items.cancel()

    def find_match(self, item_name: str) -> typing.Union[utils.Item, None]:
        for item in self.items:
            if ''.join(item_name.split()) in ''.join(item.name.split()):
                return item

    @vbu.command(name='shop', aliases=['store', 'itemshop'])
    async def _shop_command(self, ctx: vbu.Context, *, item: typing.Optional[str] = None):
        """
        Buy some shit innit
        """

        link = "https://www.youtube.com/watch?v=FP23VU01fz8"
        if item:
            item = self.find_match(item)
            if not item:
                return await ctx.reply(self.item_not_exist, mention_author=False)

            with vbu.Embed(title=item.name, use_random_colour=True) as embed:
                story_string = "\n> ".join(item.lore.story)
                name = random.choice(
                    [
                        'Obama',
                        'Jesus',
                        'Local bitchboy',
                        'Average pp bot enjoyer',
                    ]
                )

                embed.set_thumbnail(self.bot.get_emoji(item.emoji).url)
                footer_item_name = "".join(item.name.split()[0])
                embed.set_footer(f'{ctx.prefix}buy {footer_item_name} [amount]/["max"] | {ctx.prefix}iteminfo {footer_item_name}')
                embed.description = ''.join(
                    (
                        f'{item.lore.description}\n\n> {story_string}\n> - {name}\n\n',
                        f'**AUCTIONABLE:** [{"Yes" if item.auctionable else "No"}]({link})\n',
                        f'**FOR SALE:** [{"Yes" if item.shopsettings.for_sale else "No"}]({link})',
                    )
                )
                if item.shopsettings.for_sale:
                    embed.description += "\n**BUY:** [{0.buy} inches]({1})\n**SELL:** [{0.sell} inches]({1})".format(item.shopsettings, link)

                if item.used_for:
                    embed.add_field('usage:', '- ' + '\n- '.join(item.pretty_usage()))

                if item.requires:
                    embed.add_field('Skills requires:', ', '.join(item.pretty_requirements()))

                return await ctx.reply(embed=embed, mention_author=False)

        def formatter(menu, items):
            output = []
            item: utils.Item
            for item in items:
                story_string = "\n".join(item.lore.story)
                item_description = ''.join(
                    (
                        '{0} **{1.name}** ─ {1.shopsettings.buy} inches\n',
                        '[{1.type}](https://www.youtube.com/watch?v=FP23VU01fz8)',
                        ' ─ {1.lore.description}\n*{2}*',
                    )
                )
                output.append(item_description.format(self.bot.get_emoji(item.emoji), item, story_string))
            output_string = "\n\n\n" + "\n\n".join(output)
            embed = vbu.Embed()
            embed.add_field('shop', output_string)
            embed.set_footer(f'Page {menu.current_page + 1}/{menu.max_pages}')
            return embed

        p = vbu.Paginator(self.items, per_page=3, formatter=formatter, remove_reaction=True)
        await p.start(ctx, timeout=30)

    @vbu.command(name='buy')
    async def _buy_command(self, ctx: vbu.Context, *, item_name:str):
        """
        buy some shit from the shop mhm
        """
        async with vbu.DatabaseConnection() as db:
            async with utils.Pp.fetch(db, ctx.author.id, True) as pp:
                item_name_split = item_name.split()
                if len(item_name_split) > 1:
                    if item_name_split[-1] in ['all', 'max', 'maximum', 'everything']:
                        item = self.find_match(''.join(item_name_split[:-1]))
                        if not item:
                            return await ctx.reply(self.item_not_exist, mention_author=False)
                        amount = pp.size // item.shopsettings.buy

                    elif item_name_split[-1].isdigit():
                        await ctx.send(''.join(item_name_split[:-1]))
                        item = self.find_match(''.join(item_name_split[:-1]))
                        if not item:
                            return await ctx.reply(self.item_not_exist, mention_author=False)
                        amount = int(item_name_split[-1])

                    else:
                        item = self.find_match(item_name)
                        if not item:
                            return await ctx.reply(self.item_not_exist, mention_author=False)
                        amount = 1
                else:
                    amount = 1
                    item = self.find_match(item_name)
                    if not item:
                        return await ctx.reply(self.item_not_exist, mention_author=False)

                if amount < 1:
                    return await ctx.reply(f'Imagine buying less than 1 of an item', mention_author=False)

                if item.shopsettings.buy > pp.size:
                    return await ctx.reply(f'Yeah no your pp is about **{item.shopsettings.buy * amount - pp.size} inches** too short for this item', mention_author=False)

                await db('''INSERT INTO user_inventory VALUES ($1, $2, $3) ON CONFLICT (user_id, name) DO UPDATE
                    SET amount = user_inventory.amount + $3''', ctx.author.id, item.name, amount)
                pp.size -= item.shopsettings.buy * amount

                with vbu.Embed() as embed:
                    embed.set_author_to_user(ctx.author, use_nick=True)
                    embed.description = f'Aight here\'s your {amount} **{item.name}** for **{item.shopsettings.buy * amount} inches**'
                    return await ctx.reply(embed=embed, mention_author=False)


def setup(bot: vbu.Bot):
    x = Shop(bot)
    bot.add_cog(x)
