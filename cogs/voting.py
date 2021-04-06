import discord
from discord.ext import commands, tasks
from userdata.utils import get_user_topgg_vote
import dbl
import toml


with open("./config.toml") as f:
    config = toml.loads(f.read())

class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""
    
    def __init__(self, bot):
        self.bot = bot
        self.token = config["dbl"]["TOKEN"]
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True) # 30 minute update go brr
    
    
    @commands.command(aliases=["vote","voted","upvote",])
    async def vote_check(self,ctx):
        voted = await get_user_topgg_vote(self.bot, ctx.author.id)
        advert = "**free 2x boost and other perks!**"
        if voted:
            return await ctx.send(f'You\'ve voted for pp bot on https://top.gg/bot/735147633076863027\nHave fun with your {advert}')
        return await ctx.send(f'You haven\'t voted for pp bot on https://top.gg/bot/735147633076863027\nYou\'re missing out on a {advert} It\'s free and takes 10 seconds!')
    
def setup(bot):
    bot.add_cog(TopGG(bot))
