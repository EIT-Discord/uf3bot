# uf³bot

## Getting started

Download the Repo:  
  ```
  git clone https://github.com/MartinKist/uf3bot.git
  ```

Install requirements:  
  ```
  pip3 install -r requirements.txt
  ```
  
Get yourself a discord bot and -token at https://discord.com/developers/applications and paste it into `secrets.yml`:
  ```
  # secrets.yml
  
  discord: <your token here>
  ...
  ```

If you and your bot are already members of our development server you can continue to _Using the bot_.

If not, contact us or use your own server and adjust `config.yml` according to your servers roles and channels.

## Using the bot

Now everything should be ready for the bot to work properly. Just run `run.py` for the bot to start:
``` 
python3 run.py
```

or start the bot with logging level set to debug using the `--debug` flag:
``` 
python3 run.py --debug
```