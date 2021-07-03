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


class UsageRequirementNotMet(commands.CheckFailure):
    """
    Generic error for when a item requirement isn't met.
    """

    def __init__(self, usage):
        self.usage = usage


def has_skill(name: str, level: int):
    """
    Check if user has specific skill.
    """

    async def predicate(ctx: vbu.Context):
        async with vbu.DatabaseConnection() as db:
            fetched = await db('''
                SELECT level FROM user_skill
                WHERE user_id = $1 AND name = $2''', ctx.author.id, name)
        if not fetched:
            raise SkillRequirementNotMet(name, level, 0)
        if not fetched[0]['level'] >= level:
            raise SkillRequirementNotMet(name, level, fetched[0]['level'])
        return True
    return commands.check(predicate)


def has_item(name: str):
    """
    Check if user has specific item.
    """

    async def predicate(ctx: vbu.Context):
        async with vbu.DatabaseConnection() as db:
            fetched = await db('''
                SELECT * FROM user_inventory
                WHERE user_id = $1 AND name = $2 AND amount > 0''', ctx.author.id, name)
            if not fetched:
                raise ItemRequirementNotMet(name)
            return True
    return commands.check(predicate)


def has_item_with_usage(usage: typing.Optional[str]):
    """
    Check if user has an item with a specific usage.
    """

    async def predicate(ctx: vbu.Context):
        async with vbu.DatabaseConnection() as db:
            fetched = await db('''
                SELECT name FROM user_inventory
                WHERE user_id = $1 AND amount > 0''', ctx.author.id)
            if not fetched:
                raise UsageRequirementNotMet(usage)

            user_item_names = [i['name'] for i in fetched]
            items = await db('''SELECT * FROM items''')
            for i in [item['name'] for item in items if usage in item['used_for']]:
                if i in user_item_names:
                    return True
            raise UsageRequirementNotMet(usage)
    return commands.check(predicate)
