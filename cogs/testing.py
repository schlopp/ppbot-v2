import voxelbotutils as vbu
from cogs import utils
from discord.ext import commands


class TestingCommands(vbu.Cog):

    @vbu.command(name='fish')
    @utils.checks.has_item('wobbly fishing rod')
    async def _test1(self, ctx:vbu.Context):
        """
        Testing command 1
        """

        await ctx.send("You apparently have a fishing rod!")
    
    @_test1.error
    async def _test_error(self, ctx:vbu.Context, error):
        if isinstance(error, utils.checks.ItemRequirementNotMet):
            return await ctx.send(f'You need a **{error.item_name}** to run this command.')

    @vbu.command(name='bigfish')
    @utils.checks.has_item('wobbly fishing rod')
    @utils.checks.has_skill('FISHING', 1)
    async def _test2(self, ctx:vbu.Context):
        """
        Testing command 1
        """

        await ctx.send("You apparently have a fishing rod!")
    
    @_test2.error
    async def _test_error(self, ctx:vbu.Context, error):
        if isinstance(error, utils.checks.ItemRequirementNotMet):
            return await ctx.send(f'You need a **{error.item_name}** to run this command.')
        if isinstance(error, utils.checks.SkillRequirementNotMet):
            return await ctx.send(f'You need **{error.skill_name} {error.required_value}** to run this command. Your current level is **{error.current_value}**.')

def setup(bot:vbu.Bot):
    x = TestingCommands(bot)
    bot.add_cog(x)
