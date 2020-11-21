from discord.ext import commands

from core.utils import is_admin


class ModTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, context):
        return is_admin(context.author)

    @commands.group()
    async def clean(self, context, *amount: int):
        def check(msg):
            if msg.author == self.bot.user:
                pass
