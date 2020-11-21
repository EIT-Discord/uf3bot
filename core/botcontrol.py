from discord.ext import commands
from discord.ext.commands import ExtensionNotFound, ExtensionNotLoaded, ExtensionAlreadyLoaded

from core.utils import is_admin


class BotControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, context):
        return is_admin(context.author)

    async def cog_after_invoke(self, context):
        self.bot.save_config()

    @commands.command()
    async def prefix(self, context, prefix: str):
        self.bot.command_prefix = prefix
        msg = await context.channel.send(f"_Prefix changed to {prefix}._")

    @commands.command()
    async def presence(self, context, *, presence: str):
        await self.bot.set_presence(presence)
        msg = await context.channel.send(f"_Presence changed to {presence}._")

    @commands.command()
    async def config(self, context):
        await context.channel.send(f'```{str(self.bot.print_config())}```')

    @commands.command()
    async def load(self, context, module: str):
        try:
            self.bot.load_extension('modules.' + module)
            self.bot.modules.append(module)
            msg = await context.channel.send(f'_Module {module} successfully loaded._')
        except ExtensionNotFound:
            msg = await context.channel.send(f'_No module named {module} found!_')
        except ExtensionAlreadyLoaded:
            msg = await context.channel.send(f'_Module {module} already loaded!_')

    @commands.command()
    async def unload(self, context, module: str):
        try:
            self.bot.unload_extension('modules.' + module)
            self.bot.modules.remove(module)
            msg = await context.channel.send(f'_Module {module} successfully unloaded._')
        except ExtensionNotFound:
            msg = await context.channel.send(f'_No module named {module} found!_')
        except ExtensionNotLoaded:
            msg = await context.channel.send(f'_No module named {module} loaded!_')

    @commands.command()
    async def reload(self, context, module: str):
        try:
            self.bot.reload_extension('modules.' + module)
            msg = await context.channel.send(f'_Module {module} successfully reloaded._')
        except ExtensionNotFound:
            msg = await context.channel.send(f'_No module named {module} found!_')
        except ExtensionNotLoaded:
            msg = await context.channel.send(f'_No module named {module} loaded!_')
