# pylint: disable=unused-variable
# pylint: enable=too-many-lines

import discord
from discord.ext import commands
import random
import json
from customjson import load, update



class errors(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    



    #@commands.Cog.listener()
    #@commands.bot_has_permissions(send_messages=True)
    #async def on_command(self, ctx):
        #data = load('./levels.json')
        #exp_gain = random.randint(1,3)
        #if str(ctx.author.id) not in data.keys():
        #    data[str(ctx.author.id)] = {"exp":0,"rank":"Newbie"}
        #data[str(ctx.author.id)]["exp"] += exp_gain
        #data[str(ctx.author.id)]["rank"] = "GOD" if data[str(ctx.author.id)]["exp"] > 1000 else "big pp" if data[str(ctx.author.id)]["exp"] > 500 else "Newbie"
        
        #update(data,'./levels.json')
        #await ctx.send(f'{ctx.author.mention} gained {exp_gain} experience. They now have {data[str(ctx.author.id)]} Exp.')




def setup(client):
    client.add_cog(errors(client))
