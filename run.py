import os
import pathlib
import pickle
import sys
import logging
import argparse

import discord
import yaml

from core.bot import UfffBot
from core.configvalidator import validate
from core.help import DefaultHelpCommand


__version__ = '0.2'


# set up argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='start the bot and set logging level to debug', action='store_true')
parser.add_argument('--config', help='specify a different config file and start the bot')
args = parser.parse_args()


# set up logging
if args.debug:
    loglvl = logging.DEBUG
else:
    loglvl = logging.WARNING

logging.basicConfig(format='%(levelname)s:%(message)s', level=loglvl)


# load configuration
if args.config:
    configpath = args.config
else:
    configpath = 'config.yml'

try:
    with open(configpath, 'r') as file:
        config = validate(yaml.load(file, Loader=yaml.Loader))
except FileNotFoundError:
    logging.warning('No configuration file found')


# make sure data directory exists
datapath = pathlib.Path(__file__).absolute().parent/'data'
if not os.path.isdir(datapath):
    os.mkdir(datapath)


# set discord intents
intents = discord.Intents.default()
intents.members = True
intents.reactions = True


# load discord token
try:
    with open('token.pickle', 'rb') as file:
        token = pickle.load(file)
except FileNotFoundError:
    logging.error('No discord token found, use tokenpickler.py to set one')
    sys.exit(1)


print("-------------------------")
print(f"Discord.py version: {discord.__version__}")
print(f"Ufffbot version: {__version__}")
print("-------------------------")


# start bot
bot = UfffBot('', config, datapath, intents=intents, help_command=DefaultHelpCommand())
try:
    bot.run(token)
except discord.LoginFailure:
    logging.error('discord token seems to be invalid')
    sys.exit(1)
