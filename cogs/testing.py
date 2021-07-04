import voxelbotutils as vbu

from cogs import utils


class TestingCommands(vbu.Cog):

    @vbu.command()
    async def addgod(self, ctx: vbu.Context):
        item = utils.Item(
            name='god himself lmao',
            type='TOTEM',
            shopsettings=utils.ShopSettings(True, buy=10_000, sell=2_000),
            rarity='LEGENDARY', auctionable=True, emoji=826952082371772423,
            lore=utils.Lore(
                'No use! Just for testing!',
                [
                    'how the fuck did god manage to get into this game? Oh well',
                    'Very sexy i must admit',
                ],
            ),
            requires=utils.Dict({'BEGGING': 10})
        )
        async with vbu.DatabaseConnection() as db:
            await db('''DELETE FROM items WHERE name = $1''', 'god himself lmao')
            await item.create(db)


def setup(bot: vbu.Bot):
    x = TestingCommands(bot)
    bot.add_cog(x)
