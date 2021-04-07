import discord
from discord.ext import commands
import userdata as ud
import os
import toml
from importlib import reload

#prefixes
bot = commands.AutoShardedBot(command_prefix=[
    'pp ',
    'Pp ',
    'PP'
],case_insensitive=True,owner_id=393305855929483264)
bot.load_extension('jishaku')
bot.remove_command('help')
for filename in os.listdir("./cogs"):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

#status
@bot.event
async def on_connect():
    await bot.change_presence(activity=discord.Game(name="Connecting.."))
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f"pp help | pp new | grow your pp today~! ({len(bot.shard_ids) if bot.shard_ids else 0} shards, in {len(bot.guilds)} servers, with {len(await ud.fetch('user_id','userdata.pp'))} current users)"))
    print('Bot ready!')
@bot.event
async def on_guild_join(guild):
    ppchannel = bot.get_channel(816767268217290752)
    await ppchannel.send(f"Bot joined new server: {guild.name}")
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed=discord.Embed(title="pp bot has joined the game",description="Sup guys its me, pp bot. **Type** `pp help` **to get a nice lil list of commands. Type** `pp new` **to create a pp.** Have fun!\n\n**[Invite the pp bot](https://discord.com/oauth2/authorize?client_id=735147633076863027&scope=bot&permissions=104713793)**\n**[Join the pp bot server](https://discord.gg/VnSyg3J)**"))
        break
@bot.event
async def on_guild_remove(guild):
    ppchannel = bot.get_channel(816767268217290752)
    await ppchannel.send(f"Bot left server: {guild.name}")
    
@commands.command()
@commands.is_owner()
async def rld(ctx, extension):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if not is_owner:
        return
    if extension == 'all':
        loadmsg = await ctx.send(f'```\nReloading every single cog...\n```')
        newmsg = '```py\n'
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    bot.unload_extension(f'cogs.{filename[:-3]}')
                except:
                    pass
                bot.load_extension(f'cogs.{filename[:-3]}')
                newmsg += f'{filename} reloaded.\n'
        await loadmsg.edit(content=f'{newmsg}\nReloaded all of the cogs!\n```')
        return
    unloadmsg = await ctx.send(f'```\nReloading {extension}...\n```')
    try:
        bot.unload_extension(f'cogs.{extension}')
    except:
        pass
    bot.load_extension(f'cogs.{extension}')
    await unloadmsg.edit(content=f'```\nReloaded {extension}!\n```')
bot.add_command(rld)
@commands.command()
@commands.is_owner()
async def uld(ctx, extension):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if not is_owner:
        return
    if extension == 'all':
        unloadmsg = await ctx.send(f'```\nUnloading every single cog...\n```')
        newmsg = '```py\n'
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                bot.unload_extension(f'cogs.{filename[:-3]}')
                newmsg += f'{filename} reloaded.\n'
        await unloadmsg.edit(content=f'{newmsg}\nUnloaded all of the cogs!\n```')
        return
    unloadmsg = await ctx.send(f'```\nUnloading {extension}...\n```')
    bot.unload_extension(f'cogs.{extension}')
    await unloadmsg.edit(content=f'```\nUnloaded {extension}!\n```')
bot.add_command(uld)
@bot.command()
async def status(ctx, *, informationthatineed):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if not is_owner:
        return
    message = ctx.message
    if informationthatineed == 'normal':
        await bot.change_presence(activity=discord.Game(name=f"pp help | pp new | grow your pp today~! ({len(bot.shard_ids) if bot.shard_ids else 0} shards, in {len(bot.guilds)} servers, with {len(await ud.fetch('user_id','userdata.pp'))} current users)"))
        await message.add_reaction('👌')
        return
    await bot.change_presence(activity=discord.Game(name=informationthatineed))
    await message.add_reaction('👌')


@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 pong! Latency: `{round(bot.latency, 8)}ms`')
    
@bot.command()
async def invite(ctx):
    await ctx.send(embed=discord.Embed(description='**[Invite the pp bot](https://discord.com/oauth2/authorize?client_id=735147633076863027&scope=bot&permissions=104713793)**'))
    
@bot.command(aliases=['github'])
async def git(ctx):
    await ctx.send(embed=discord.Embed(description='**[pp bot github](https://github.com/schlopp/ppbot)**'))
    
@bot.command(aliases=['server'])
async def support(ctx):
    await ctx.send('https://discord.gg/VnSyg3J')
    
@bot.command(aliases=['reloaduserdata'])
async def rldud(ctx):
    reload(ud)
    await ctx.send('Done')

if __name__ == '__main__':
    with open("config.toml") as f:
        config = toml.loads(f.read())
                                  
    bot.start(
        config['admin']['TOKEN'],
        reconnect=True,
    )
    
