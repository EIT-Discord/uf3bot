from PIL import Image, ImageDraw
import numpy as np

import discord
from discord.ext import commands

from modules.Games.pillar import Tile, Pillar
from core.interbed import InteractiveEmbed


class VierGewinnt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp = self.bot.temppath/'vg.png'  # TODO: dynamische namen, für mehrere sessions
        self.pillar = Pillar((700, 600), background_color='blue', spacing=10)

        # game specific
        self.players = {}
        self.board = np.array([Empty() for i in range(7 * 6)]).reshape((7, 6))

        # Interactive Embed
        self.interbed = None

    def on_btn_1(self, button, member):
        pass

    @commands.command('vier')
    async def start(self, context, player2: discord.User):
        self.players[1] = context.author
        self.players[2] = player2

        self.interbed = InteractiveEmbed(self.bot, self.bot.imageserver, context.channel)

        self.interbed.add_button('1️⃣', callback=self.on_btn_1)
        """self.interbed.add_button('two', callback=self.on_btn_2)
        self.interbed.add_button('three', callback=self.on_btn_3)
        self.interbed.add_button('four', callback=self.on_btn_4)
        self.interbed.add_button('five', callback=self.on_btn_5)
        self.interbed.add_button('six', callback=self.on_btn_6)
        self.interbed.add_button('seven', callback=self.on_btn_7)"""

        img = self.pillar.plot(self.board)
        img.save(self.temp)

        self.interbed.load_image(self.temp, filename='vg.png')
        self.interbed.set_image('vg.png')

        await self.interbed.start()


class Chip(Tile):
    def __init__(self, player):
        self.player = player
        self.assets = {1: Image.open('1.png'), 2: Image.open('2.png')}

    def get_img(self, idx):
        if self.player == 1:
            color = 'red'
        else:
            color = 'yellow'

        img = Image.new('RGBA', (100, 100), (255, 0, 0, 0))
        canv = ImageDraw.Draw(img)
        canv.ellipse((0, 0, 100, 100), fill=color)

        return img


class Empty(Tile):
    def get_img(self, idx):
        img = Image.new('RGBA', (100, 100), (255, 0, 0, 0))
        canv = ImageDraw.Draw(img)
        canv.ellipse((0, 0, 100, 100), fill='white')
        return img
