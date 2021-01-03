import pickle


token = input('new token: ')


with open('token.pickle', 'wb') as file:
    pickle.dump(token, file)
    print('new token successfully set.')
