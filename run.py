import pathlib
import pickle
import discord
import sys

from core.bot import UffBot
from core.help import DefaultHelpCommand


__version__ = '0.2'


DATAPATH = pathlib.Path(__file__).absolute().parent/'data'


# set discord intents
intents = discord.Intents.default()
intents.members = True
intents.reactions = True

# try to load the discord token
try:
    with (DATAPATH/'dctoken.pickle').open('rb') as file:
        token = pickle.load(file)
except FileNotFoundError:
    print('No discord-token found, use data/tokenpickler.py to set one. Aborting start')
    sys.exit()


print("-------------------------")
print(f"Discord.py version: {discord.__version__}")
print(f"Uffbot version: {__version__}")
print("-------------------------")


# start bot
bot = UffBot('', DATAPATH, intents=intents, help_command=DefaultHelpCommand())
bot.run(token)
