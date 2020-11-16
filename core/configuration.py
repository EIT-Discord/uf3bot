import pathlib
import pickle
import discord
from discord.ext import commands

from core.utils import delete_messages


DATAPATH = pathlib.Path(__file__).absolute().parent.parent / 'data'


def get_config():
    try:
        with (DATAPATH / 'botconfig.pickle').open('rb') as file:
            config = pickle.load(file)
        print('Config loaded successfully:')
        print(config)
    except FileNotFoundError:
        print('No bot configuartion found. Using default settings.')
        config = Config()
    return config


class Config:
    def __init__(self):
        self.prefix = '!'
        self.admin_prefix = '?'
        self.presence = ''

    async def load(self, bot):
        bot.prefix = self.prefix
        bot.admin_prefix = self.admin_prefix
        bot.command_prefix = (self.admin_prefix, self.prefix)

        bot.presence = self.presence
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(self.presence))

    def save(self, bot):
        self.prefix = bot.prefix
        self.admin_prefix = bot.admin_prefix
        self.presence = bot.presence

        with (DATAPATH / 'botconfig.pickle').open('wb') as file:
            pickle.dump(self, file)

    def __str__(self):
        output = ''
        for key, value in self.__dict__.items():
            output += f'{key}: {value}\n'
        return output[:-1]


class BotControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        if ctx.prefix == self.bot.admin_prefix:
            try:
                if ctx.author.guild_permissions.administrator:
                    return True
            except AttributeError:
                pass
        return False

    @commands.command()
    async def prefix(self, context, prefix: str):
        if prefix == self.bot.admin_prefix:
            msg = await context.channel.send("_This prefix is already used as admin prefix, "
                                             "please choose another prefix._")
        else:
            self.bot.prefix = prefix
            self.bot.command_prefix = (self.bot.admin_prefix, prefix)
            self.bot.config.save(self.bot)
            msg = await context.channel.send("_Prefix changed successfully._")
        await delete_messages(msg, context.message)

    @commands.command()
    async def admin_prefix(self, context, admin_prefix: str):
        if admin_prefix == self.bot.prefix:
            msg = await context.channel.send("_This prefix is already used as standard prefix, "
                                             "please choose another prefix._")
        else:
            self.bot.admin_prefix = admin_prefix
            self.bot.command_prefix = (admin_prefix, self.bot.config.prefix)
            self.bot.config.save(self.bot)
            msg = await context.channel.send("_Admin prefix changed successfully._")
        await delete_messages(msg, context.message)

    @commands.command()
    async def presence(self, context, *, presence: str):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(presence))
        self.bot.presence = presence
        self.bot.config.save(self.bot)
        msg = await context.channel.send("_Presence changed successfully._")
        await delete_messages(msg, context.message)

    @commands.command()
    async def config(self, context):
        await context.channel.send(f'```{str(self.bot.config)}```')
