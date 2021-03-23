
import discord
from discord.ext import commands
import random
import userdata as ud



class shoptest(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.command(aliases=['store'])
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
                embed.add_field(name=f'**{i.item_name}** ─ __{await i.price(pp)} inches__ ─ `{await i.item_type()}`',value=f'{await i.item_desc()}{" | The price of this item depends on your current multiplier" if await i.multiplierdependent() else ""}',inline=False)
            embed.set_footer(text=f'page {page}/{totalpages}')
        return await ctx.send(embed=embed)


    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def buy(self, ctx, amount:int, *, item:str):
        embed = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])))
        pp = ud.Pp(ctx.author.id)
        inv = ud.Inv(ctx.author.id)
        item = ud.Shop.Item(item.lower())
        shop = ud.Shop()
        #no pp
        if not await pp.check():
            embed.description = f"{ctx.author.mention}, you need a pp first! Get one using `pp new`!"
            return await ctx.send(embed=embed)
        #yes pp
        amount = 1 if amount < 1 else amount
        #no item
        if item.item_name.lower() not in [i.item_name.lower() for i in await shop.items()]:
            embed.description = f'{ctx.author.mention}, **`"{item.item_name}"`** is not something for sale at the moment. Check out `pp shop` to see what\'s currently available'
            return await ctx.send(embed=embed)
        #yes item
        #broke boi
        if await pp.pp_size() < amount*await item.price(pp):
            embed.description = f"{ctx.author.mention}, your pp isnt big enough! You need **{await item.price(pp)*amount-await pp.pp_size()} more inches** to buy this item! Type `pp grow` to grow your pp."
            return await ctx.send(embed=embed)
        #rich boi
        if await item.item_type() == "MULTIPLIER":
            await pp.size_add(-1*amount*await item.price(pp))
            await pp.multiplier_add(amount*await item.gain())
            embed.description = f"*{ctx.author.mention} takes the **pills** and feels a strong power going thru their body. They now have a {await pp.multiplier()} multiplier.*"
            return await ctx.send(embed=embed)
        if await item.item_type() in ["TOOL","ITEM"]:
            await pp.size_add(-1*amount*await item.price(pp))
            await inv.new_item(item.item_name,amount)
            embed.description = f"{ctx.author.mention}, you now have {f'**{amount}**' if amount>1 else 'a'} new **{item.item_name+'s' if amount>1 else item.item_name}!**"
            return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(shoptest(bot))
