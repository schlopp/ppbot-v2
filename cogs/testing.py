import voxelbotutils as vbu
from cogs import utils
from discord.ext import commands


class TestingCommands(vbu.Cog):

    @vbu.command(name='fish')
    @utils.checks.has_item_with_usage('FISHING')
    async def _test1(self, ctx:vbu.Context):
        """
        Testing command 1
        """

        await ctx.send("You cast your rod.. but nothing happens? Weird. Almost like this is just a test command!", components=vbu.MessageComponents(vbu.ActionRow(vbu.Button('test!','HELLO'))))
    
    @_test1.error
    async def _test1_error(self, ctx:vbu.Context, error):
        if isinstance(error, utils.checks.ItemRequirementNotMet):
            return await ctx.send(f'You need a **{error.item_name}** to run this command.')
        if isinstance(error, utils.checks.SkillRequirementNotMet):
            return await ctx.send(f'You need **{error.skill_name} {error.required_level}** to run this command. Your current level is **{error.current_level}**.')
        if isinstance(error, utils.checks.UsageRequirementNotMet):
            return await ctx.send(f'You need an item with **{error.usage}** to run this command. Too bad!')

    @vbu.command(name='bigfish')
    @utils.checks.has_skill('FISHING', 3)
    async def _test2(self, ctx:vbu.Context):
        """
        Testing command 2
        """

        await ctx.send("You apparently have a fishing rod!")
    
    @_test2.error
    async def _test2_error(self, ctx:vbu.Context, error):
        if isinstance(error, utils.checks.ItemRequirementNotMet):
            return await ctx.send(f'You need a **{error.item_name}** to run this command.')
        if isinstance(error, utils.checks.SkillRequirementNotMet):
            return await ctx.send(f'You need **{error.skill_name} {error.required_level}** to run this command. Your current level is **{error.current_level}**.')
        if isinstance(error, utils.checks.UsageRequirementNotMet):
            return await ctx.send(f'You need an item with **{error.usage}** to run this command. Too bad!')
    
    @vbu.command(name='createtestitem')
    @commands.is_owner()
    async def _create_test_item(self, ctx:vbu.Context):
        """
        Create test item
        """

        item = utils.Item('wobbly fishing rod', type='TOOL', shopsettings=utils.ShopSettings(True, buy=100, sell=20),
                        rarity='COMMON', auctionable=False, emoji='🎣', used_for=['FISHING'],
                        recipes=utils.Dict({'sturdy fishing rod':5}), lore=utils.Lore('We all gotta start somewhere.',
                        ['This rod kinda looks like it\'d break first fling']))
        await item.create()

def setup(bot:vbu.Bot):
    x = TestingCommands(bot)
    bot.add_cog(x)
