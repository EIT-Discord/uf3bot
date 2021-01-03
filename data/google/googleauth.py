import pickle
import os.path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

tokenpath = 'token.pickle'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

creds = None
if os.path.exists(tokenpath):
    with open(tokenpath, 'rb') as token:
        creds = pickle.load(token)

# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(tokenpath, 'wb') as token:
        pickle.dump(creds, token)
