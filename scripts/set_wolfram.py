import pickle
from pathlib import Path
import sys
from os import rename

# the bots /data directory
datapath = Path(__file__).parent.parent.absolute()/'data'
tokenpath = datapath/'wolfram_token.pickle'


new_token = input('new token: ')

# if a dctoken.pickle file already exists, rename it to dctoken_old.pickle
# if that file already exists aswell, exit the script without doing anything
try:
    rename(datapath / 'wolfram_token.pickle', datapath / 'wolfram_token_old.pickle')
    print('existing wolfram_token.pickle was renamed to wolfram_token_old.pickle')
except FileNotFoundError:
    pass
except FileExistsError:
    print('wolfram_token.pickle as well as wolfram_token_old.pickle already exist.\n'
          'Delete, move or rename one of these files and restart the script to set a new token.')
    sys.exit()

with tokenpath.open('wb') as file:
    pickle.dump(new_token, file)
    print('new token successfully set.')
