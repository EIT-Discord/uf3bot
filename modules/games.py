from discord.ext import commands

from core.interbed import ImageServer
from modules.Games.viergewinnt import VierGewinnt


def setup(bot):
    bot.add_cog(Games(bot))


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.imageserver = ImageServer(self.bot.datapath/'InteractiveEmbed', 'sers-mahlzeit.de')
        self.datapath = self.bot.datapath/'games'

        bot.add_cog(VierGewinnt(bot))