import discord
from discord.ext import commands
import random
import userdata as ud



class shoptest(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.command(aliases=['storetest'])
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def shoptest(self, ctx, page:int=1):
        async with ctx.typing():
            embed,pp,exception = await ud.create_embed(ctx)
            if exception:
                return await ud.handle_exception(ctx,exception)
            shop = ud.Shop()
            shopitems = await shop.items()
            totalpages = len(shopitems) // 5 + (len(shopitems) % 5 > 0)
            #yes pp
            #page bad
            if page < 1 or page > totalpages:
                embed.description = f"{ctx.author.mention}, that page is doesn't exist."
                return await ctx.send(embed=embed)
            #page good
            embed.title = "shop"
            embed.description = f'In the shop you can buy items with inches. You currently have **{await pp.pp_size()}** inches.\n Type `pp buy <amount> <item>` to buy an item. Prices of items may change depending on how many you\'ve bought'
            for i in shopitems[page * 5 - 5:page * 5]:
                embed.add_field(
                    name=f'**{i.item_name}** ─ __{await i.price(pp)} inches__ ─ `{await i.item_type()}` ─ selling for {await i.sell_for()} inches',
                    value=f'{await i.item_desc()}{" | The price of this item depends on your current multiplier" if await i.multiplierdependent() else ""}',inline=False)
            embed.set_footer(text=f'page {page}/{totalpages}')
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(shoptest(bot))
