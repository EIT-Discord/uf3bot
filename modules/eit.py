import pickle
from discord.ext import commands


def setup(bot):
    bot.add_cog(EIT(bot))


class EIT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.configpath = self.bot.datapath/'eitconfig.pickle'

        self.guild = None
        self.student_role = None
        self.rules_channel = None

        self.semester = []

        self.load_config()

    def cog_check(self, ctx):
        if ctx.prefix == self.bot.prefix:
            return True
        return False

    def load_config(self):
        try:
            with self.configpath.open('rb') as file:
                config = pickle.load(file)
            self.__dict__.update(config)
            print('EIT configuration loaded successfully:')
            print(config)
        except FileNotFoundError:
            print('No EIT configuartion found. A server has to be set up first.')

    def save_config(self):
        config = self.__dict__
        config.pop('bot')

        with self.configpath.open('wb') as file:
            pickle.dump(config, file)

    @commands.command()
    async def eit(self, context):
        await context.channel.send('_Hier könnte ihre Werbung stehen!_')


class Semester:
    """ Represents a semester

        Attributes
        -----------
        name:                   Display name of the semester
        study_groups:           List of discord.role.Role objects representing the study_groups
        announcement_channel:   discord.TextChannel object used for announcements
        """

    def __init__(self):
        self.name = ''
        self.study_groups = []
        self.announcement_channel = None
