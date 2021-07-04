import typing
import discord

import voxelbotutils as vbu
from discord.ext import commands

from cogs import utils


class Visual(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)

    @vbu.command(name='inventory', aliases=['inv', 'items', 'storage'])
    async def _display_inventory(self, ctx: vbu.Context, member: typing.Optional[discord.Member] = None):
        """
        Check what's in your inventory
        """

        await ctx.trigger_typing()
        if member is None:
            member = ctx.author

        async with vbu.DatabaseConnection() as db:
            inventory = await db('''SELECT name, amount FROM user_inventory WHERE user_id = $1 AND amount > 0''', member.id)
            if not inventory:
                if member == ctx.author:
                    return await ctx.reply('You have no items lmao get good <:LULW:854752425348694016>', mention_author=False)
                return await ctx.reply(f'**{member.display_name}** legit has no items <:LULW:854752425348694016>', mention_author=False)

            items = []
            inventory_names = [i['name'] for i in inventory]
            for item in await utils.fetch_items(db):
                if item.name in inventory_names:
                    item.amount = [i['amount'] for i in inventory if i['name'] == item.name][0]
                    items.append(item)

        def formatter(menu, items):
            output = []
            for item in items:
                output.append(f'{self.bot.get_emoji(item.emoji)} **{item.name}** ─ {item.amount}\n{item.type} ─ {item.lore.description}')
            output_string = "\n\n".join(output)
            embed = vbu.Embed(title=f"{member.display_name}'s inventory")
            embed.add_field('Items', output_string)
            embed.set_footer(f'Page {menu.current_page + 1}/{menu.max_pages}')
            return embed

        p = vbu.Paginator(items, per_page=5, formatter=formatter, remove_reaction=True)
        await p.start(ctx, timeout=30)


def setup(bot: vbu.Bot):
    x = Visual(bot)
    bot.add_cog(x)
