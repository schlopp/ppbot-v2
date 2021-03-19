# pylint: disable=unused-variable
# pylint: enable=too-many-lines

import discord
from discord.ext import commands
import asyncio
import random
import io
import json
import aiohttp
import asyncpraw as praw
import userdata as ud



class animals(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.reddit = praw.Reddit(client_id="6BHhUI735hQNaA",client_secret="hi6RSWw_JFHWePcJsrpJ9hd4-wJlzA",user_agent="pp_bot:%s:1.0"%"hi6RSWw_JFHWePcJsrpJ9hd4-wJlzA")
        self.cute_message = ['very cute', '10/10', ]
        
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://aws.random.cat/meow') as r:
                if r.status == 200:
                    js = await r.json()
                    e = discord.Embed(title=random.choice(self.cute_message+['meow', ]))
                    e.set_image(url=js['file'])
                    await ctx.send(embed=e)
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://dog.ceo/api/breeds/image/random') as r:
                if r.status == 200:
                    js = await r.json()
                    e = discord.Embed(title=random.choice(self.cute_message+['woof!', 'good boy', ]))
                    e.set_image(url=js['message'])
                    await ctx.send(embed=e)
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def fox(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://randomfox.ca/floof/') as r:
                if r.status == 200:
                    js = await r.json()
                    e = discord.Embed(title=random.choice(self.cute_message+['sneaky boy', 'good boy', ]))
                    e.set_image(url=js['image'])
                    await ctx.send(embed=e)
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def panda(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://some-random-api.ml/img/panda/') as r:
                if r.status == 200:
                    js = await r.json()
                    e = discord.Embed(title=random.choice(self.cute_message+['GIANT AND ROUND.', ]))
                    e.set_image(url=js['link'])
                    await ctx.send(embed=e)
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def redpanda(self, ctx, panda:str=None):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://some-random-api.ml/img/red_panda/') as r:
                if r.status == 200:
                    js = await r.json()
                    e = discord.Embed(title=random.choice(self.cute_message))
                    e.set_image(url=js['link'])
                    await ctx.send(embed=e)
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def meme(self, ctx):
        async with ctx.channel.typing():
            embed,pp,exception = await ud.create_embed(ctx,pp_dependent=False,include_tip=False,item_required="meme machine")
            if exception:
                return await ud.handle_exception(ctx,exception)
            subreddit = await self.reddit.subreddit(random.choice(['dankmemes','memes']))
            memes = []
            async for i in subreddit.hot(limit=50) :
                if not i.stickied:
                    memes.append(i)
            meme = random.choice(memes)
            embed.title = meme.title
            embed.set_image(url=meme.url)
        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(animals(bot))