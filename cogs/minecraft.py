import discord
from discord.ext import commands
import userdata as ud
import asyncio
import os

import pyautogui
import pydirectinput


class Minecraft(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.game = None
    
    @commands.group(name="mc",invoke_without_command=True)
    @commands.is_owner()
    async def mc(self, ctx):
        async with ctx.typing():
            await asyncio.sleep(.1)
        return await ctx.send('```asciidoc\n= Minecraft Control Help =\nA list of commands\n=====\n- pp mc start```')
    
    @mc.command(name="launch")
    @commands.is_owner()
    async def mc_launcher(self, ctx):
        os.startfile("D:\\Games\\Minecraft\\MinecraftLauncher.exe")
        return await ctx.send('The Minecraft launcher has been started.')
    
    @mc.command(name="start")
    @commands.is_owner()
    async def mc_start(self, ctx):
        os.startfile("D:\\Games\\Minecraft\\MinecraftLauncher.exe")
        await ctx.send('The Minecraft launcher has been started! Type `1` when the launcher is done loading.')
        try:
            message = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.content == '1',
                timeout = 60.0,
                )
            pydirectinput.click(1053, 751)
            await ctx.send('Minecraft is being started! Type the name of your world when you\'re on the main menu.')
            message = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author,
                timeout = 60.0,
                )
            # open single player, create new world
            pydirectinput.click(955, 534)
            await asyncio.sleep(1)
            pydirectinput.click(1112, 699)
            await asyncio.sleep(1)
            
            #select text
            pydirectinput.keyDown('ctrl')
            pydirectinput.press('a')
            pydirectinput.keyUp('ctrl')
            pydirectinput.write(message.content,0.1)
            
            #create world
            pydirectinput.click(789, 746)
            message = await ctx.send('Your world is generating. React to this message with movement!')
            await message.add_reaction('⬅️')
            await message.add_reaction('⬆️')
            await message.add_reaction('⬇️')
            await message.add_reaction('➡️')
        except asyncio.TimeoutError:
            return
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        emoji, user = self.parse_reaction_payload(payload)
        print('react pog')
        if user.id not in self.bot.owner_ids or reaction.message.channel.id != 816345282714796092:
            return
        moves = {
            '⬅️':'a',
            '⬆️':'w',
            '⬇️':'s',
            '➡️':'d',
        }
        print(reaction.emoji)
        try:
            pydirectinput.keyDown(moves[reaction.emoji])
        except KeyError:
            pass
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction:discord.Reaction, user):
        print('no react pog')
        if user.id not in self.bot.owner_ids or reaction.message.id != self.game:
            return
        moves = {
            '⬅️':'a',
            '⬆️':'w',
            '⬇️':'s',
            '➡️':'d',
        }
        try:
            pydirectinput.keyUp(moves[reaction.emoji])
        except KeyError:
            pass
    
    #
    @mc.command(name="starte")
    @commands.is_owner()
    async def mc_starte(self, ctx):
        async with ctx.typing():
            pydirectinput.click(373, 768)
            await asyncio.sleep(1)
            pydirectinput.click(303, 587)
            await asyncio.sleep(1)
            pydirectinput.click(1053, 751)
        return await ctx.send('Minecraft is being started.')
    
    @mc.command(name="sp")
    @commands.is_owner()
    async def mc_singleplayer(self, ctx, *, name:str="I'm cool"):
        async with ctx.typing():
            # open single player, create new world
            pydirectinput.click(955, 534)
            await asyncio.sleep(1)
            pydirectinput.click(1112, 699)
            await asyncio.sleep(1)
            
            #select text
            pydirectinput.keyDown('ctrl')
            pydirectinput.press('a')
            pydirectinput.keyUp('ctrl')
            pydirectinput.write(name,0.1)
            
            #create world
            pydirectinput.click(789, 746)
        return await ctx.send('Your world is generating.')
    
    @mc.command(name="walk")
    @commands.is_owner()
    async def mc_walk(self, ctx):
        async with ctx.typing():
            pydirectinput.keyDown('w')
        return await ctx.send('Walking')
    
    @mc.command(name="nowalk")
    @commands.is_owner()
    async def mc_nowalk(self, ctx):
        async with ctx.typing():
            pydirectinput.keyUp('w')
        return await ctx.send('Stopped walking')
    
    @mc.command(name="walkleft")
    @commands.is_owner()
    async def mc_walkleft(self, ctx):
        async with ctx.typing():
            pydirectinput.keyDown('a')
        return await ctx.send('Walking left')
    
    @mc.command(name="nowalkleft")
    @commands.is_owner()
    async def mc_nowalkleft(self, ctx):
        async with ctx.typing():
            pydirectinput.keyUp('a')
        return await ctx.send('Stopped walking left')
    
    @mc.command(name="walkright")
    @commands.is_owner()
    async def mc_walkright(self, ctx):
        async with ctx.typing():
            pydirectinput.keyDown('d')
        return await ctx.send('Walking right')
    
    @mc.command(name="nowalkright")
    @commands.is_owner()
    async def mc_nowalkright(self, ctx):
        async with ctx.typing():
            pydirectinput.keyUp('d')
        return await ctx.send('Stopped walking right')
    
    @mc.command(name="walkback")
    @commands.is_owner()
    async def mc_walkback(self, ctx):
        async with ctx.typing():
            pydirectinput.keyDown('s')
        return await ctx.send('Walking right')
    
    @mc.command(name="nowalkback")
    @commands.is_owner()
    async def mc_nowalkback(self, ctx):
        async with ctx.typing():
            pydirectinput.keyUp('s')
        return await ctx.send('Stopped walking right')
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction:discord.Reaction, user:discord.Member):
        if user.id not in self.bot.owner_ids or reaction.message.id != self.game:
            return
        




def setup(bot):
    bot.add_cog(Minecraft(bot))