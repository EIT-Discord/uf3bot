import pickle
import discord
import sys

from core.configuration import DATAPATH


__version__ = '0.2'


# set discord intents
from core.uffbot import UffBot

intents = discord.Intents.default()
intents.members = True

# try to load the discord token
try:
    with (DATAPATH/'dctoken.pickle').open('rb') as file:
        token = pickle.load(file)
except FileNotFoundError:
    print('No discord-token found, use scripts/set_token.py to set one. Aborting start')
    sys.exit()


print("-------------------------")
print(f"Discord.py version: {discord.__version__}")
print(f"Uffbot version: {__version__}")
print("-------------------------")


# start bot
bot = UffBot('', intents=intents)
bot.run(token)
