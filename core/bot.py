import pickle
import discord
from discord.ext.commands import bot, ExtensionNotFound

from core.botcontrol import BotControl
from core.moderation import ModTools


class UffBot(bot.Bot):
    def __init__(self, command_prefix, datapath, **kwargs):
        super().__init__(command_prefix, **kwargs)

        # datapaths
        self.datapath = datapath
        self.configpath = self.datapath / 'botconfig.pickle'

        # default config
        self.prefix = '!'
        self.admin_prefix = '?'
        self.presence = ''
        self.modules = []
        self.owner_ids = set()

        # this set determines which attributes of the bot will be saved and loaded
        self.attributes_to_save = {'prefix',
                                   'admin_prefix',
                                   'presence',
                                   'modules',
                                   'owner_ids'}

    async def on_ready(self):
        print("-------------------------")
        print('Logged in as')
        print(f"{str(self.user)}, {self.user.id}")
        print("-------------------------")

        # load bot settings
        self.load_config()

        # adding core cogs
        self.add_cog(BotControl(self))
        self.add_cog(ModTools(self))

        print('Bot fully initialized, using following settings:')
        print(self.print_config())

    def save_config(self):
        config_to_save = {}
        for key, val in self.__dict__.items():
            if key in self.attributes_to_save:
                config_to_save.update({key: val})

        with self.configpath.open('wb') as file:
            pickle.dump(config_to_save, file)

    def print_config(self):
        output = ''
        for key, value in self.__dict__.items():
            if key in self.attributes_to_save:
                output += f'{key}: {value}\n'
        return output[:-1]

    def load_config(self):
        try:
            with self.configpath.open('rb') as file:
                config = pickle.load(file)
            self.__dict__.update(config)
        except FileNotFoundError:
            print('No bot configuration found. Using default settings.')

        self.set_prefix()  # needs to be called, to set the already loaded prefixes

        # try to load modules from config
        for module in self.modules:
            try:
                self.load_extension('modules.' + module)
            except ExtensionNotFound:
                print(f'No module named {module} found. Ignoring module import.')

    def set_prefix(self, prefix=None, admin_prefix=None):
        if prefix:
            self.prefix = prefix
        if admin_prefix:
            self.admin_prefix = admin_prefix

        self.command_prefix = (self.prefix, self.admin_prefix)

    async def set_presence(self, presence):
        await self.change_presence(status=discord.Status.online, activity=discord.Game(presence))
        self.presence = presence
