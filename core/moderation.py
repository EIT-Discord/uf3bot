from discord.ext import commands
from core.utils import check_pinned, UserInputEvent, is_admin


class ModTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @is_admin()
    async def clean(self, context):
        """Löscht alle Nachrichten, die nicht angepinnt wurden"""
        await context.channel.send('Möchtest du wirklich alle Nachrichten löschen?')
        message = await UserInputEvent.create(context.bot, context.channel, context.author)
        if message.content.lower() in ['ja', 'yes']:
            await context.channel.purge(check=check_pinned, limit=500)

    @commands.command()
    @is_admin()
    async def clear(self, context, amount: int):
        """Löscht die angegebene Anzahl an Nachrichten"""
        await context.channel.purge(check=check_pinned, limit=amount+1)
