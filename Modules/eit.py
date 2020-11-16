from discord.ext import commands


class EIT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        if ctx.prefix == self.bot.prefix:
            return True
        return False

    @commands.command()
    def setup(self, context):
        pass