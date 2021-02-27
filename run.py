import os
import pathlib
import sys
import logging
import argparse

import discord
import yaml

from core.bot import UfffBot
from core.configvalidator import validate
from core.help import DefaultHelpCommand


__version__ = '0.3'


# set up argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='start the bot and set logging level to debug', action='store_true')
args = parser.parse_args()


# set up logging
if args.debug:
    loglvl = logging.DEBUG
else:
    loglvl = logging.WARNING

logging.basicConfig(format='%(levelname)s:%(message)s', level=loglvl)


# load config file
try:
    with open('config.yml', 'r') as file:
        config = validate(yaml.load(file, Loader=yaml.Loader))
except FileNotFoundError:
    logging.warning('No configuration file found')


# make sure data directory exists
datapath = pathlib.Path(__file__).absolute().parent/'data'
if not os.path.isdir(datapath):
    os.mkdir(datapath)


# load secrets file
try:
    with open('secrets.yml', 'r') as file:
        secrets = yaml.load(file, Loader=yaml.Loader)
except FileNotFoundError:
    logging.error('No secrets file found.')
    sys.exit(1)

# get discord token
try:
    token = secrets['discord']
    if not token:
        raise KeyError
except KeyError:
    logging.error('No discord token found in secrets file.')
    sys.exit(1)


print("-------------------------")
print(f"Discord.py version: {discord.__version__}")
print(f"Ufffbot version: {__version__}")


# set discord intents
intents = discord.Intents.default()
intents.members = True
intents.reactions = True

# start bot
bot = UfffBot('!', config, secrets, datapath, intents=intents, help_command=DefaultHelpCommand())
try:
    bot.run(token)
except discord.LoginFailure:
    logging.error('discord token seems to be invalid')
    sys.exit(1)
