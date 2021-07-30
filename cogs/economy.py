import asyncio
import typing
import random
import string
from datetime import datetime

import voxelbotutils as vbu
import discord
from discord.ext import tasks

from cogs import utils


class Economy(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.shop_items: typing.List[utils.Item] = []
        self.auction_items: typing.List[utils.Item] = []
        self.items: typing.List[utils.Item] = []
        self.load_items.start()
        self.item_not_exist = 'cmonbruh that item doesn\'t exist what are you DOING'
        self.link = 'https://www.youtube.com/watch?v=FP23VU01fz8'
        self.skills = {}

    @tasks.loop(minutes=10)
    async def load_items(self):
        async with vbu.DatabaseConnection() as db:
            self.shop_items = await utils.fetch_items(db, for_sale=True)
            self.auction_items = await utils.fetch_items(db, auctionable=True)
            self.items = await utils.fetch_items(db)

    def cog_unload(self):
        self.load_items.cancel()

    def find_shop_match(self, item_name: str) -> typing.Optional[utils.Item]:
        for item in self.shop_items:
            if ''.join(item_name.split()) in ''.join(item.name.split()):
                return item
    
    async def get_cached_skill(self, db: vbu.DatabaseConnection, user_id: int, name: str):
        if (user_id, name) in self.skills:
            return self.skills[(user_id, name)]
        v = await db('''SELECT * FROM user_skill WHERE user_id = $1 AND name = $2''', user_id, name)
        if v:
            self.skills[(user_id, name)] = {
                'user_id': v[0]['user_id'],
                'name': v[0]['name'],
                'level': utils.get_level_by_exp(v[0]['experience']),
                'experience': v[0]['experience'],
            }
        else:
            self.skills[(user_id, name)] = {
                'user_id': user_id,
                'name': name,
                'level': utils.get_level_by_exp(0),
                'experience': 0,
            }
        return self.skills[(user_id, name)]
    
    async def update_cached_skill(self, db: vbu.DatabaseConnection, user_id: int, name: str, experience: int):
        v = await db('''
            INSERT INTO user_skill (user_id, name, experience) VALUES ($1, $2, $3)
            ON CONFLICT (user_id, name) DO UPDATE SET experience = user_skill.experience + $3
            RETURNING *
            ''', user_id, name, experience)

        self.skills[(user_id, name)] = {
            'user_id': v[0]['user_id'],
            'name': v[0]['name'],
            'level': utils.get_level_by_exp(v[0]['experience']),
            'experience': v[0]['experience'],
        }

    @vbu.command(name='shop', aliases=['store', 'itemshop'])
    @vbu.cooldown.cooldown(1, 10)
    async def _shop_command(self, ctx: vbu.Context, *, item: typing.Optional[str] = None):
        """
        Buy some shit innit
        """
        
        await ctx.trigger_typing()
        if item:
            item = self.find_shop_match(item)
            if not item:
                return await ctx.reply(self.item_not_exist, mention_author=False)

            with vbu.Embed(title=item.name, use_random_colour=True) as embed:
                story_string = "\n> ".join(item.lore.story)

                embed.set_thumbnail(self.bot.get_emoji(item.emoji).url)
                footer_item_name = "".join(item.name.split()[0])
                embed.set_footer(f'{ctx.prefix}buy {footer_item_name} [amount]/["max"] | {ctx.prefix}iteminfo {footer_item_name}')
                embed.description = '\n'.join((
                    f'{item.lore.description}\n\n> {story_string}\n> - {utils.random_name()}\n',
                    f'**AUCTIONABLE:** [{"Yes" if item.auctionable else "No"}]({self.link})',
                    f'**FOR SALE:** [{"Yes" if item.shopsettings.for_sale else "No"}]({self.link})',
                    ))

                if item.shopsettings.for_sale:
                    embed.description += "\n**BUY:** [{0.buy} inches]({1})\n**SELL:** [{0.sell} inches]({1})".format(item.shopsettings, self.link)

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

        p = vbu.Paginator(self.shop_items, per_page=3, formatter=formatter, remove_reaction=True)
        await p.start(ctx, timeout=30)

    @vbu.command(name='buy')
    @vbu.cooldown.cooldown(1, 10)
    async def _buy_command(self, ctx: vbu.Context, *, item_name:str):
        """
        buy some shit from the shop mhm
        """

        await ctx.trigger_typing()
        async with vbu.DatabaseConnection() as db:
            async with utils.Pp.fetch(db, ctx.author.id, True) as pp:
                item_name_split = item_name.split()
                if len(item_name_split) > 1:
                    if item_name_split[-1] in ['all', 'max', 'maximum', 'everything']:
                        item = self.find_shop_match(''.join(item_name_split[:-1]))
                        if not item:
                            return await ctx.reply(self.item_not_exist, mention_author=False)
                        item.amount = pp.size // item.shopsettings.buy

                    elif item_name_split[-1].isdigit():
                        await ctx.send(''.join(item_name_split[:-1]))
                        item = self.find_shop_match(''.join(item_name_split[:-1]))
                        if not item:
                            return await ctx.reply(self.item_not_exist, mention_author=False)
                        item.amount = int(item_name_split[-1])

                    else:
                        item = self.find_shop_match(item_name)
                        if not item:
                            return await ctx.reply(self.item_not_exist, mention_author=False)
                        item.amount = 1
                else:
                    item = self.find_shop_match(item_name)
                    if not item:
                        return await ctx.reply(self.item_not_exist, mention_author=False)
                    item.amount = 1

                if item.amount < 1:
                    return await ctx.reply(f'Imagine buying less than 1 of an item', mention_author=False)

                if item.shopsettings.buy > pp.size:
                    return await ctx.reply(f'Yeah no your pp is about **{item.shopsettings.buy * item.amount - pp.size} inches** too short for this item', mention_author=False)

                await db('''
                    INSERT INTO user_inventory VALUES ($1, $2, $3) ON CONFLICT (user_id, name) DO UPDATE
                    SET amount = user_inventory.amount + $3''', ctx.author.id, item.name, item.amount)
                pp.size -= item.shopsettings.buy * item.amount

                with vbu.Embed() as embed:
                    embed.set_author_to_user(ctx.author, use_nick=True)
                    embed.description = f'Aight here\'s {utils.readable_list(bot=self.bot, items=[item])} for **{item.shopsettings.buy * item.amount} inches**'
                    return await ctx.reply(embed=embed, mention_author=False)

    @vbu.command(name='inventory', aliases=['inv', 'items', 'storage'])
    async def _display_inventory(self, ctx: vbu.Context, member: typing.Optional[discord.Member] = None):
        """
        Check what's in your inventory
        """

        await ctx.trigger_typing()
        member = member or ctx.author
        async with vbu.DatabaseConnection() as db:
            inventory = await db('''SELECT name, amount FROM user_inventory WHERE user_id = $1 AND amount > 0''', member.id)
            if not inventory:
                if member == ctx.author:
                    return await ctx.reply('You have no items lmao get good <:LULW:854752425348694016>', mention_author=False)
                return await ctx.reply(f'**{member.display_name}** legit has no items <:LULW:854752425348694016>', mention_author=False)

            items = []
            inventory_names = [i['name'] for i in inventory]
            for item in self.items:
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

    @vbu.command(name='show', aliases=['display', 'get', 'view'])
    async def _display_pp_command(self, ctx: vbu.Context, user: typing.Optional[discord.Member] = None):
        """
        Show that bad boy to the whole wide world
        """

        await ctx.trigger_typing()
        user = user or ctx.author
        async with vbu.DatabaseConnection() as db:
            async with utils.Pp.fetch(db, user.id, False) as pp:
                with vbu.Embed(use_random_colour=True) as embed:
                    embed.set_author(name=f'{pp.name} ({user.display_name}\'s pp)')
                    embed.description = '\n'.join((
                        f'```ini\n[ 8{("=" * (pp.size // 50 + 1))[:400]}D ]```\n**Stats:**\nSize: {pp.size} inches\nMultiplier: {pp.multiplier}x',
                        f'Inventory: [type `{ctx.prefix}inv`]({self.link})',
                    ))
                    v = await db('''SELECT name, experience FROM user_skill WHERE user_id = $1 AND experience > 0''', ctx.author.id)
                    if v:
                        embed.add_field('Skills', '\n'.join([f"{v[0]['name'].title()}: {utils.get_level_by_exp(v[0]['experience'])} ({v[0]['experience']} EXP)"]))
                return await ctx.reply(embed=embed, mention_author=False)

    @vbu.command(name='beg', aliases=['plead'])
    async def _beg_command(self, ctx: vbu.Context):
        """
        Beg for some inches like the dirty drifter you are
        """
        
        await ctx.trigger_typing()
        async with vbu.DatabaseConnection() as db:
            async with utils.Pp.fetch(db, ctx.author.id) as pp:
                with vbu.Embed(use_random_colour=True) as embed:
                    person = utils.random_name(include_url=True)
                    embed.set_author(name=person[0], icon_url=person[1])
                
                
                skill = await self.get_cached_skill(db, ctx.author.id, 'BEGGING')
                locations = utils.BeggingLocations(
                    utils.BeggingLocation(
                        0, 'BRIDGE', '😔', 'Under a Bridge', 'Lmao broke boy go beg with the other homeless', [
                            'Damn bro I live under a bridge and you\'re asking ME for inches??',
                            'What did you think was gonna happen when you asked some homeless dude for inches',
                            'Sorry I spent all my inches on meth'
                        ]),
                    utils.BeggingLocation(
                        1, 'MARKET', '🧑‍🌾', 'Farmer\'s Market', 'Time to annoy those fucking farmers', [
                            'Step aside silly beggar, I have vegetables to sell',
                            'I\'m trying to sell my vegetables stop bothering me',
                            'Please just let me sell my fruits in peace',
                        ]),
                    utils.BeggingLocation(
                        2, 'BLOCK', '🏙️', 'City Block', '\'m sure the residents have some inches to spare', [
                            'I\'m so sick of this shit. I spend 4.050 inches a month on rent and can\'t afford food. Fuck you, you aren\'t getting anything',
                            'Get off my block',
                            'Oh go to hell, tourist',
                        ]),
                    utils.BeggingLocation(
                        3, 'CLUB', '<a:poledance:870466180253618196>', 'Adult dance club', 'Kids, look away!', [
                            'Just because I don\'t have clothes on doesn\'t mean you can just steal my pp',
                            'I expect a good show before I give you anything',
                        ]),
                    utils.BeggingLocation(
                        4, 'AUCTION', '🖼️', 'Art Auction', 'Let\'s scam these rich losers', [
                            'Oh my god get away from me, I\'m WAY too rich to talk to you',
                            'My dog only drinks bottled water',
                            'Do you know who I am!? I have money! I\'m important! Get away from me!',
                            'Stop asking for handouts, I never got help from anyone',
                            'I don\'t even have any inches! I replaced my pp with gold!',
                            'I don\'t have any inches to spare, I only have a few billion left. Hey, you know what\'s a good idea? Your kids should WORK for my kids!',
                            'Oh please, I\'m broke! The gas to fly my private jet is getting expensive'
                            'GET THE FUCK OUT LMAO. I\'M RICH, BITCH!',
                            'You\'re wasting your time. Go do poor people things, like paying taxes',
                            'I refuse to donate to someone with a house worth less than 10 million USD',
                            'Ew, you\'re way too poor! I\'m gonna go buy a new Bugatti, I\'m getting tired of this Mercedes',
                        ]),
                )

                components = vbu.MessageComponents(vbu.ActionRow(
                    locations.to_selectmenu()
                ))

                m: vbu.InteractionMessageable = await ctx.reply('**Where are you begging?**\nLeveling up `Begging` unlocks new locations', components=components, mention_author=False)
                try:
                    p = await self.bot.wait_for("component_interaction", check=lambda p: p.message.id == m.id and p.user.id == ctx.author.id, timeout=15)
                except asyncio.TimeoutError:
                    await m.edit(components=None, mention_author=False)
                    return await ctx.send(f'{ctx.author.mention} you left me on read:pensive:')

                await p.ack()
                chosen_location = [x for x in locations.locations if x.id == p.values[0]][0]
                if not random.randint(0, 9): # haha no inches for you
                    embed.description = f'“{random.choice(chosen_location.quotes)}”'
                    return await m.edit(content=None, components=None, embed=embed, mention_author=False)

                exp_growth = random.randint(int(10 * (1 + chosen_location.level / 10)), int(16 * 1 + chosen_location.level / 10))
                await self.update_cached_skill(db, ctx.author.id, 'BEGGING', exp_growth)
                skill = await self.get_cached_skill(db, ctx.author.id, 'BEGGING')
                embed.set_footer(f"+{exp_growth} begging XP (Begging {utils.int_to_roman(skill['level'])})")
                
                growth = random.randint(10 * (1 + chosen_location.level), 20 * ( 1 + chosen_location.level))
                quote = random.choice([
                    'Your pp is so small I feel bad, take {0}, now go away',
                    'Yeah whatever mate take {0}',
                    'You\'re so annoying, here, have {0}. Now scram! Skedaddle!',
                    'Eh why not, here\'s {0}. Have a nice day!'
                ])

                if random.randint(0,1):
                    item = random.choice([i for i in self.shop_items if i.shopsettings.buy < 500])
                    item.amount = random.randint(1, 2)
                    embed.description = f'“{quote.format(utils.readable_list(self.bot, size=growth, items=[item]))}”'
                    return await m.edit(content=None, components=None, embed=embed, mention_author=False)

                embed.description = f'“{quote.format(utils.readable_list(self.bot, size=growth))}”'
                return await m.edit(content=None, components=None, embed=embed, mention_author=False)


def setup(bot: vbu.Bot):
    x = Economy(bot)
    bot.add_cog(x)
