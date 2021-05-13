import discord
from discord.ext import commands
from datetime import datetime
import random
import userdata as ud



class shop(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.command(aliases=['store'])
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @ud.has_pp()
    async def shop(self, ctx, page:int=1):
        async with ctx.typing():
            embed = await ud.create_embed(ctx)
            pp = await ud.Pp.fetch(ctx.author.id, self.bot)
            shop = await ud.Shop.fetch(pp.default_multiplier)
            totalpages = len(shop.keys()) // 5 + (len(shop.keys()) % 5 > 0)
            #yes pp
            #page bad
            if page < 1 or page > totalpages:
                embed.description = f"{ctx.author.mention}, that page is doesn't exist."
                return await ctx.send(embed=embed)
            #page good
            embed.title = "shop"
            embed.description = f'In the shop you can buy items with inches. You currently have **{pp.size}** inches.\n Type `pp buy <amount> <item>` to buy an item. Prices of items may change depending on how many you\'ve bought'
            for i in list(shop.items())[page * 5 - 5:page * 5]:
                embed.add_field(
                    name = f'**{i[0]}** ─ __{i[0]["price"]} inches__ ─ `{i[0]["type"]}`',value=f'{i[0]["description"]}{" | The price of this item depends on your current multiplier" if i[0]["multiplier_dependent"] else ""}',
                    inline = False
                )
            embed.set_footer(text=f'page {page}/{totalpages}')
        return await ctx.send(embed=embed)
    

    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @ud.has_pp()
    async def buy(self, ctx, amount, *, item:str):
        embed = await ud.create_embed(ctx)
        pp = await ud.Pp.fetch(ctx.author.id, self.bot)
        shop = await ud.Shop.fetch(pp.default_multiplier)
        item = item.lower()
        
        if item not in shop.keys():
            raise ud.ShopItemNotFound(f'{ctx.author.mention}, **`"{item}"`** is not for sale at the moment. Check out the shop to see what\'s currently available')
            return await ctx.send(embed=embed)
                                
        try:
            amount = int(amount)
        except ValueError:
            if amount == 'max':
                amount = pp.size // shop[item]["price"]
            else:
                raise commands.BadArgument()
        if amount < 1:
            embed.description = f'{ctx.author.mention}, you can\'t buy less than 1 of an item?????'
            return await ctx.send(embed=embed)
        
        
        if pp.size < amount * shop[item]["price"]:
            raise ud.AmountNotEnough(f"{ctx.author.mention}, your pp isnt big enough! You need **{shop[item]["price"] * amount - pp.size} more inches** to buy this item! Type `pp grow` to grow your pp.")
            return await ctx.send(embed=embed)
        
        
        pp.size += -amount * shop[item]["price"]
        if await shop[item]["type"] == "MULTIPLIER":
            pp.default_multiplier += amount * shop[item]["gain"]
            await pp.update()
            embed.description = f"*{ctx.author.mention} takes the **{amount if amount > 1 else ''} {item}** and feels a strong power going through their body. Their multiplier has exapnded!"
            return await ctx.send(embed=embed)
        
        if await shop[item]["type"] in ["TOOL","ITEM"]:
            await pp.update()
            async with ud.Inv(ctx.author.id) as inv:
                inv[item] += amount
            embed.description = f"{ctx.author.mention}, you now have {f'**{amount}**' if amount>1 else 'a'} new **{item+'s' if amount>1 else item}!**"
            return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(shop(bot))
