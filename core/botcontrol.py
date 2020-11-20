from discord import User
from discord.ext import commands
from discord.ext.commands import ExtensionNotFound, ExtensionNotLoaded, ExtensionAlreadyLoaded


class BotControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, context):
        if context.prefix == self.bot.admin_prefix and await self.bot.is_owner(context.author):
            return True
        else:
            return False

    async def cog_after_invoke(self, context):
        self.bot.save_config()

    @commands.command()
    async def add_admin(self, context, user: User):
        self.bot.owner_ids.add(user.id)
        msg = await context.channel.send(f"_{user.name} is now a bot administrator._")

    @commands.command()
    async def remove_admin(self, context, user: User):
        try:
            self.bot.owner_ids.remove(user.id)
            msg = await context.channel.send(f"_{user.name} is not a bot administrator anymore._")
        except KeyError:
            msg = await context.channel.send(f"_{user.name} is not a bot administrator!_")

    @commands.command()
    async def prefix(self, context, prefix: str):
        if prefix == self.bot.admin_prefix:
            msg = await context.channel.send("_This prefix is already used as admin prefix, "
                                             "please choose another prefix!_")
        else:
            self.bot.set_prefix(prefix=prefix)
            msg = await context.channel.send(f"_Prefix changed to {prefix}._")

    @commands.command()
    async def admin_prefix(self, context, admin_prefix: str):
        if admin_prefix == self.bot.prefix:
            msg = await context.channel.send("_This prefix is already used as standard prefix, "
                                             "please choose another prefix!_")
        else:
            self.bot.set_prefix(admin_prefix=admin_prefix)
            msg = await context.channel.send(f"_Admin prefix changed to {admin_prefix}._")

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
