from discord.ext import commands
from discord.ext.commands import ExtensionNotFound, ExtensionNotLoaded, ExtensionAlreadyLoaded

from core.utils import is_admin


class BotControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_after_invoke(self, context):
        self.bot.save_config()

    @commands.group(name='bot')
    @is_admin()
    async def control_bot(self, context):
        pass

    @control_bot.command()
    async def prefix(self, context, prefix: str):
        """Ändert den Befehls-Prefix"""
        self.bot.command_prefix = prefix
        await context.channel.send(f"_Prefix changed to {prefix}._")

    @control_bot.command()
    async def presence(self, context, *, presence: str):
        """Ändert die Discord-Presence des Bots"""
        await self.bot.set_presence(presence)
        await context.channel.send(f"_Presence changed to {presence}._")

    @control_bot.command()
    async def config(self, context):
        """Zeigt die aktuelle Einstellung des Bots"""
        await context.channel.send(f'```{str(self.bot.print_config())}```')

    @control_bot.command()
    async def load(self, context, module: str):
        """Läd ein Bot-Modul"""
        try:
            self.bot.load_extension('modules.' + module)
            self.bot.modules.append(module)
            await context.channel.send(f'_Module "{module}" successfully loaded._')
        except ExtensionNotFound:
            await context.channel.send(f'_No module named "{module}" found!_')
        except ExtensionAlreadyLoaded:
            await context.channel.send(f'_Module "{module}" already loaded!_')
        except:
            # If an error gets cought here, it means that the module that was tried to be loaded has some erroneous code
            await context.channel.send(f'_Something went wrong while loading module "{module}", Ignoring import_')

    @control_bot.command()
    async def unload(self, context, module: str):
        """Entfernt ein geladenes Bot-Modul"""
        try:
            self.bot.unload_extension('modules.' + module)
            self.bot.modules.remove(module)
            await context.channel.send(f'_Module {module} successfully unloaded._')
        except ExtensionNotFound:
            await context.channel.send(f'_No module named {module} found!_')
        except ExtensionNotLoaded:
            await context.channel.send(f'_No module named {module} loaded!_')

    @control_bot.command()
    async def reload(self, context, module: str):
        """Läd ein geladenes Modul neu"""
        try:
            self.bot.reload_extension('modules.' + module)
            await context.channel.send(f'_Module {module} successfully reloaded._')
        except ExtensionNotFound:
            await context.channel.send(f'_No module named {module} found!_')
        except ExtensionNotLoaded:
            await context.channel.send(f'_No module named {module} loaded!_')
