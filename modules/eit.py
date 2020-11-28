import asyncio

import yaml
from discord.ext import commands
from discord.utils import get

from core.utils import is_admin_check
from modules.EIT.calendar import Calendar
from modules.EIT.roles import Roles
from modules.EIT.setup import setup_dialog
from modules.EIT.utils import get_member


def setup(bot):
    bot.add_cog(EIT(bot))


class EIT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.guilds[0]
        self.configpath = self.bot.datapath / 'eitconfig.pickle'

        # eitconfig
        self.student_role_id = None
        self.semester = []
        self.game_roles = {}
        self.admin_calendar = None

        self.import_config()

        self.bot.add_listener(self.on_member_join)
        self.bot.add_cog(Roles(self))
        self.bot.add_cog(Calendar(self))

    def print_config(self):
        output = ''
        for key, value in self.__dict__.items():
            output += f'{key}: {value}\n'
        return output[:-1]

    def import_config(self):
        try:
            with (self.bot.datapath / 'eitconfig.yml').open('r') as file:
                config = yaml.load(file, Loader=yaml.Loader)
        except FileNotFoundError:
            print('No EIT configuration found. Using default settings')
            return

        self.student_role_id = config['student_id']

        for semester in config['semester'].values():
            announcement_channel = get(self.guild.channels, id=semester['announcement_channel'])
            # TODO: study_groups as discord roles
            new_semester = Semester(semester['name'], announcement_channel, semester['groups'])
            self.semester.append(new_semester)

        self.game_roles = config['game_roles']
        self.admin_calendar = get(self.guild.channels, id=config['admin_calendar'])

    @commands.group()
    @is_admin_check()
    async def eit(self, context):
        pass

    @eit.command()
    async def load(self, context):
        self.import_config()
        await context.channel.send('_Config successfully loaded._')

    @eit.command()
    async def config(self, context):
        await context.channel.send('```' + self.print_config() + '```')

    async def on_member_join(self, member):
        await setup_dialog(self, member)

    @commands.command()
    async def setup(self, context):
        member = get_member(self.bot, context.author)
        await setup_dialog(self, member)


class Semester:
    """ Represents a semester

        Attributes
        -----------
        name:                   Display name of the semester
        study_groups:           List of discord.role.Role objects representing the study_groups
        announcement_channel:   discord.TextChannel object used for announcements
        """

    def __init__(self, name, announcement_channel, study_groups):
        self.name = name
        self.study_groups = study_groups
        self.announcement_channel = announcement_channel