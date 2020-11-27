from discord.ext import commands


class ModTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def clean(self, context):
        await context.channel.purge(limit=500)
