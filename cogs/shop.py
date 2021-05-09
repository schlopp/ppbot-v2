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
            embed.description = f'In the shop you can buy items with inches. You currently have **{pp.size}** inches.\n Type `pp buy <amount> <item>` to buy an item. Prices of items may change depending on how many you\'ve bought'
            for i in shopitems[page * 5 - 5:page * 5]:
                embed.add_field(name=f'**{i.item_name}** ─ __{await i.price(self.bot, pp)} inches__ ─ `{await i.item_type()}`',value=f'{await i.item_desc()}{" | The price of this item depends on your current multiplier" if await i.multiplierdependent() else ""}',inline=False)
            embed.set_footer(text=f'page {page}/{totalpages}')
        return await ctx.send(embed=embed)
    

    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @ud.has_pp()
    async def buy(self, ctx, amount, *, item:str):
        embed = await ud.create_embed(ctx)
        pp = await ud.Pp.fetch(ctx.author.id, self.bot)
        item = ud.Shop.Item(item.lower())
        shop = ud.Shop()
        
        if item.item_name not in [i.item_name.lower() for i in await shop.items()]:
            embed.description = f'{ctx.author.mention}, **`"{item.item_name}"`** is not something for sale at the moment. Check out `pp shop` to see what\'s currently available'
            return await ctx.send(embed=embed)
                                
        if amount == 'max':
            amount = pp.size // await item.price(self.bot, pp)
        try:
            amount = int(amount)
        except ValueError:
            raise commands.BadArgument()
        if amount < 1:
            embed.description = f'{ctx.author.mention}, you can\'t buy less than 1 of an item?????'
            return await ctx.send(embed=embed)
        
        
        if pp.size < amount * await item.price(self.bot, pp):
            embed.description = f"{ctx.author.mention}, your pp isnt big enough! You need **{await item.price(self.bot, pp) * amount - pp.size} more inches** to buy this item! Type `pp grow` to grow your pp."
            return await ctx.send(embed=embed)
        
        
        pp.size += -amount * await item.price(self.bot, pp)
        if await item.item_type() == "MULTIPLIER":
            pp.default_multiplier += amount * await item.gain()
            await pp.update()
            embed.description = f"*{ctx.author.mention} takes the **{amount} {item.item_name}** and feels a strong power going through their body. Their multiplier has exapnded!"
            return await ctx.send(embed=embed)
        
        if await item.item_type() in ["TOOL","ITEM"]:
            await pp.update()
            async with ud.Inv(ctx.author.id) as inv:
                inv[item.item_name] += amount
            embed.description = f"{ctx.author.mention}, you now have {f'**{amount}**' if amount>1 else 'a'} new **{item.item_name+'s' if amount>1 else item.item_name}!**"
            return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(shop(bot))
