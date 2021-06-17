import typing
import discord
import voxelbotutils as vbu
from cogs import utils
from discord.ext import commands


class Visual(vbu.Cog):

    @vbu.command(name='inventory', aliases=['inv', 'items', 'storage'])
    async def _display_inventory(self, ctx:vbu.Context, member:typing.Optional[discord.Member]=None):
        """
        Testing command 1
        """

        await ctx.trigger_typing()
        if member is None:
            member = ctx.author
        async with vbu.DatabaseConnection() as db:
            user_inventory = await db('''SELECT name, amount FROM user_inventory WHERE user_id = $1 AND amount > 0''', member.id)
            all_items = await db('''SELECT * FROM items''')
        
        if not user_inventory:
            if member == ctx.author:
                return await ctx.send('You have no items <:LULW:854752425348694016>')
            return await ctx.send(f'**{member.display_name}** has no items <:LULW:854752425348694016>')
        
        # user_inventory = [
        #     utils.Item(
        #         item['name'],
        #         requires=utils.utils.Dict.from_json(item['requires']),
        #         type=item['type'],
        #         shopsettings=utils.ShopSettings.from_json(item['shopsettings']),
        #         rarity=item['rarity'],
        #         auctionable=item['auctionable'],
        #         emoji=item['emoji'],
        #         recipe=utils.utils.Dict.from_json(item['recipe']),
        #         used_for=item['used_for'],
        #         recipes=utils.utils.Dict.from_json(item['recipes']),
        #         buffs=[utils.utils.Dict.from_json(i) for i in item['buffs']],
        #         lore=utils.Lore(item['description'], item['story']),
        #         amount=
        #         )
        #     for item in all_items if item['name'] in [user_item['name'] for user_item in user_inventory]
        # ]
        user_items:typing.List[utils.Item] = []
        user_inventory_names = [i['name'] for i in user_inventory]
        for item in all_items:
            if item['name'] in user_inventory_names:
                amount = [i['amount'] for i in user_inventory if i['name'] == item['name']][0]
                user_items.append(
                    utils.Item(
                        item['name'],
                        requires=utils.Dict.from_json(item['requires']),
                        type=item['type'],
                        shopsettings=utils.ShopSettings.from_json(item['shopsettings']),
                        rarity=item['rarity'],
                        auctionable=item['auctionable'],
                        emoji=item['emoji'],
                        recipe=utils.Dict.from_json(item['recipe']),
                        used_for=item['used_for'],
                        recipes=utils.Dict.from_json(item['recipes']),
                        buffs=[utils.Dict.from_json(i) for i in item['buffs']],
                        lore=utils.Lore(
                            item['description'],
                            item['story'],
                        ),
                        amount=amount,
                    )
                )
        
        def formatter(menu, items):
            output = []
            for i in items:
                output.append(f'{i.emoji} **{i.name}** ─ {i.amount}\n{i.type} ─ {i.lore.description}')
            output_string = "\n\n".join(output)
            embed = vbu.Embed(title=f"**{member.display_name}'s inventory**")
            embed.add_field('Items', output_string)
            embed.set_footer(f'Page {menu.current_page + 1}/{menu.max_pages}')
            return embed

        p = vbu.Paginator(user_items, per_page=5, formatter=formatter, remove_reaction=True)
        await p.start(ctx, timeout=30)

def setup(bot:vbu.Bot):
    x = Visual(bot)
    bot.add_cog(x)
