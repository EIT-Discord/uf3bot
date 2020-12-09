import itertools
import discord
from discord.ext.commands import HelpCommand

from core.utils import codeblock


class DefaultHelpCommand(HelpCommand):
    """The implementation of the default help command."""

    def __init__(self, **options):
        self.sort_commands = options.pop('sort_commands', True)
        self.dm_help = options.pop('dm_help', False)
        self.commands_heading = options.pop('commands_heading', "Commands:")
        self.no_category = options.pop('no_category', 'No Category')
        self.embed = discord.Embed()

        super().__init__(**options)

    def add_indented_commands(self, commands, *, heading):
        """Indents a list of commands after the specified heading."""

        if not commands:
            return

        entry = ''

        for command in commands:
            name = command.name
            entry += self.clean_prefix + name + codeblock(command.short_doc)

        self.embed.add_field(name=heading, value=entry, inline=False)

    async def send_embed(self):
        """A helper utility to send the page output from :attr:`paginator` to the destination."""
        destination = self.get_destination()
        await destination.send(embed=self.embed)

    def get_destination(self):
        ctx = self.context
        if self.dm_help is True:
            return ctx.author
        else:
            return ctx.channel

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        no_category = '\u200b{0.no_category}:'.format(self)

        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return cog.qualified_name + ':' if cog is not None else no_category

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        to_iterate = itertools.groupby(filtered, key=get_category)

        # Now we can add the commands to the page.
        for category, commands in to_iterate:
            commands = sorted(commands, key=lambda c: c.name) if self.sort_commands else list(commands)
            self.add_indented_commands(commands, heading=category)
        await self.send_embed()

    async def send_command_help(self, command):
        self.embed.add_field(name=f"{self.clean_prefix}{command.name}",
                             value=codeblock(command.short_doc), inline=False)
        await self.send_embed()

    async def send_group_help(self, group):
        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        self.add_indented_commands(filtered, heading=group.short_doc)

        await self.send_embed()

    async def send_cog_help(self, cog):
        if cog.signature:
            self.embed.add_field(name=cog.name, value=cog.signature)
        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        self.add_indented_commands(filtered, heading=self.commands_heading)
        await self.send_embed()
