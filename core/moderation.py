from discord.ext import commands
from core.utils import check_pinned


class ModTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def clean(self, context):
        """Löscht alle Nachrichten, die nicht angepinnt wurden"""
        await context.channel.purge(check=check_pinned, limit=500)
