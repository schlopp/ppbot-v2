import typing
import voxelbotutils as vbu
from discord.ext import commands


class RequirementNotMet(commands.CheckFailure):
    """
    Generic error for when a requirement isn't met.
    """


def required(name:str, value:int):
    """
    Check if bot setup is complete.
    """

    async def predicate(ctx:vbu.Context, name:str, value:int):
        async with vbu.DatabaseConnection() as db:
            fetched = db('''
            SELECT amount FROM user_inventory
            WHERE user_id = $1''', ctx.author.id)
            if fetched['amount']:
                return True
            return False
    return commands.check(predicate)
