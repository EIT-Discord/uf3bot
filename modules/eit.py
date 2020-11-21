import pickle

import yaml
from discord.ext import commands

from core.utils import is_admin
from modules.EIT.setup import StudentSetup


def setup(bot):
    bot.add_cog(EIT(bot))


class EIT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.eit = self

        self.bot.add_cog(StudentSetup(self.bot))
        self.configpath = self.bot.datapath/'eitconfig.pickle'

        self.student_role_id = None
        self.semester = []

        self.import_config()

    def cog_check(self, context):
        return is_admin(context.author)

    # def load_config(self):
    #     try:
    #         with self.configpath.open('rb') as file:
    #             config = pickle.load(file)
    #         self.__dict__.update(config)
    #         print('EIT configuration loaded successfully:')
    #         print(config)
    #     except FileNotFoundError:
    #         print('No EIT configuartion found. A server has to be set up first.')
    #
    # def save_config(self):
    #     config = self.__dict__
    #     config.remove('bot')
    #
    #     with self.configpath.open('wb') as file:
    #         pickle.dump(config, file)

    def print_config(self):
        output = ''
        for key, value in self.__dict__.items():
            output += f'{key}: {value}\n'
        return output[:-1]

    def import_config(self):
        with (self.bot.datapath / 'eitconfig.yml').open('r') as file:
            config = yaml.load(file, Loader=yaml.Loader)

        self.student_role_id = config['student_id']

        for semester in config['semester'].values():
            new_semester = Semester(semester['name'], semester['announcement_channel'], semester['groups'])
            self.semester.append(new_semester)

    @commands.group()
    async def eit(self, context):
        pass

    @eit.command()
    async def load(self, context):
        self.import_config()
        await context.channel.send('_Config successfully loaded._')

    @eit.command()
    async def config(self, context):
        await context.channel.send('```'+self.print_config()+'```')


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



