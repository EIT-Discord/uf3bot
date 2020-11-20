import pickle
from pathlib import Path

datapath = Path(__file__).parent.parent.absolute()/'data'
configpath = datapath/'botconfig.pickle'


print('This script is intended to set a bot administrator for the initial setup of the bot.\n'
      'This administrator can then add more administrators during the bots runtime.\n'
      'Note: This script overwrites any administrators you may have already set.')

admin_id = input('administrators discord-id: ')


try:
    with configpath.open('rb') as file:
        config = pickle.load(file)
except FileNotFoundError:
    config = {}

config.update({'owner_ids': {int(admin_id)}})

with configpath.open('wb') as file:
    pickle.dump(config, file)

print('administrator successfully set.')
