import pickle
import asyncio
import sys

import discord
from discord.ext.commands import bot, ExtensionNotFound, ExtensionAlreadyLoaded

from core.botcontrol import BotControl
from core.moderation import ModTools


class UffBot(bot.Bot):
    def __init__(self, command_prefix, datapath, **kwargs):
        super().__init__(command_prefix, **kwargs)

        # TODO: Kompabilität für mehr gilden
        self.guild = None

        # datapaths
        self.datapath = datapath
        self.configpath = self.datapath/'botconfig.pickle'
        self.temppath = self.datapath/'temp/'

        # default config
        self.command_prefix = '!'
        self.presence = ''
        self.modules = []

        # this set determines which attributes of the bot will be saved and loaded
        self.attributes_to_save = {'presence',
                                   'modules',
                                   'command_prefix'}

    async def on_ready(self):
        print('Logged in as')
        print(f"{str(self.user)}, {self.user.id}")
        print("-------------------------")
        print(f'https://discordapp.com/oauth2/authorize?client_id={(await self.application_info()).id}&scope=bot')

        if len(self.guilds) == 0:
            sys.exit()

        elif len(self.guilds) > 1:
            print('The bot is a member of more than one server, this may lead to unexpected behavior or errors.')

        # load bot settings
        self.load_config()

        # TODO: mehr gilden
        self.guild = self.guilds[0]

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

        # try to load modules from config
        # TODO: kaputte module handeln
        for module in self.modules:
            try:
                self.load_extension('modules.' + module)
            except ExtensionNotFound:
                self.modules.remove(module)
            except ExtensionAlreadyLoaded:
                pass
        asyncio.create_task(self.change_presence(status=discord.Status.online, activity=discord.Game(self.presence)))

    async def set_presence(self, presence):
        await self.change_presence(status=discord.Status.online, activity=discord.Game(presence))
        self.presence = presence
