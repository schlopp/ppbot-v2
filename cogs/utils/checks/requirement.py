import typing
import voxelbotutils as vbu
from discord.ext import commands


class SkillRequirementNotMet(commands.CheckFailure):
    """
    Generic error for when a skill requirement isn't met.
    """

    def __init__(self, skill_name, required_level, current_level):
        self.skill_name = skill_name
        self.required_level = required_level
        self.current_level = current_level

class ItemRequirementNotMet(commands.CheckFailure):
    """
    Generic error for when a item requirement isn't met.
    """

    def __init__(self, item_name):
        self.item_name = item_name

def has_skill(name:str, level:int):
    """
    Check if user has specific skill.
    """

    async def predicate(ctx:vbu.Context):
        async with vbu.DatabaseConnection() as db:
            fetched = await db('''
            SELECT value FROM user_skill
            WHERE user_id = $1 AND name = $2''', ctx.author.id, name)
        if not fetched:
            raise SkillRequirementNotMet(name, level, 0)
        if not fetched[0]['level'] >= level:
            raise SkillRequirementNotMet(name, level, fetched[0]['level'])
        return True
    return commands.check(predicate)

def has_item(name:str):
    """
    Check if user has specific item.
    """

    async def predicate(ctx:vbu.Context):
        async with vbu.DatabaseConnection() as db:
            fetched = await db('''
            SELECT * FROM user_inventory
            WHERE user_id = $1 AND name = $2 AND amount > 0''', ctx.author.id, name)
        if not fetched:
            raise ItemRequirementNotMet(name)
        return True
    return commands.check(predicate)