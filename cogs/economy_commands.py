import voxelbotutils as vbu


class EconomyCommands(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        self.bot = bot


def setup(bot: vbu.Bot):
    x = EconomyCommands(bot)
    bot.add_cog(x)
