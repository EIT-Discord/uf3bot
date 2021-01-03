import pickle
from io import BytesIO
from urllib.error import HTTPError

import discord
import requests
import wolframalpha
from discord.ext import commands


def setup(bot):
    bot.add_cog(Wolfram(bot))


class Wolfram(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            with (self.bot.datapath / 'wolframtoken.pickle').open('rb') as file:
                self.token = pickle.load(file)
        except FileNotFoundError:
            print('No wolfram-token found, use scripts/tokenpickler.py to set one.')
        self.wolfram_client = wolframalpha.Client(self.token)

    @commands.command()
    async def wolfram(self, context, *, query: str):
        """Suchanfrage an die WolframAlpha API"""
        try:
            res = self.wolfram_client.query(query)
        except HTTPError:
            await context.channel.send("Hoppla! Sieht so aus als wäre die Wolfram Alpha API gerade nicht verfügbar.\n"
                                       "Versuche es in ein paar minuten nochmal.")
            return

        try:
            for pod in res.pods:
                for sub in pod.subpods:
                    if sub['img']:
                        imgurl = sub['img']['@src']
                        imgtitle = f"```{pod['@title']}```"
                        binimg = BytesIO(requests.get(imgurl).content)
                        await context.channel.send(imgtitle, file=discord.File(binimg, filename='wolframalpha.png'))
        except AttributeError:
            await context.channel.send(f'```Wolfram Alpha doesn\'t understand your query: "{query}"\n'
                                       f'Try the following:\n'
                                       f'- Use different phrasing or notations\n'
                                       f'- Enter whole words instead of abbreviations\n'
                                       f'- Avoid mixing mathematical and other notations\n'
                                       f'- Check your spelling\n'
                                       f'- Give your input in English```')
