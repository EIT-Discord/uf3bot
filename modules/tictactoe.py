import discord
import numpy as np
from discord.ext import commands

from core.utils import codeblock


def setup(bot):
    bot.add_cog(TicTacToe(bot))


class TicTacToe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.guilds[0]
        self.channel = None
        self.board = None
        self.player1 = None
        self.player2 = None
        self.active_player = None
        self.symbol = None
        self.running = False

    @commands.command()
    async def tictactoe(self, context, player2: discord.User):
        """Merih der Zigeuner"""
        if self.running:
            return
        else:
            self.player1 = context.author
            self.player2 = player2
            self.symbol = 'X'
            self.active_player = self.player1
            self.channel = context.channel
            self.create_board()
            await self.send_board()
            self.bot.add_listener(self.on_message)

    async def on_message(self, message):
        if self.player2 is None:
            if message.channel == self.channel and message.author != self.player1:
                self.player2 = message.author
        elif self.valid_input(message):
            if message.content.lower() == 'stop':
                self.reset()
                await message.channel.send('Game gestoppt!')
                return
            elif message.author == self.active_player:
                try:
                    position = int(message.content)
                    self.update_board(position)
                except ValueError:
                    await self.channel.send('Not a valid input!')
                    return
                await self.check_board()
                await self.send_board()
                self.toggle_active_player()

    def create_board(self):
        self.board = np.arange(1, 10, dtype=object).reshape((3, 3))
        self.running = True

    def reset(self):
        self.channel = None
        self.board = None
        self.player1 = None
        self.player2 = None
        self.active_player = None
        self.symbol = None
        self.bot.remove_listener(self.on_message)
        self.running = False

    def update_board(self, position):
        self.board[self.board == position] = self.symbol

    def toggle_active_player(self):
        if self.active_player is not self.player1:
            self.active_player = self.player1
            self.symbol = 'X'
        else:
            self.active_player = self.player2
            self.symbol = 'O'

    def valid_input(self, message):
        if self.channel == message.channel and \
                message.author in [self.player1, self.player2]:
            return True

    async def send_board(self):
        await self.channel.send(self.board)

    async def check_board(self):
        for idx in range(3):
            if np.all(self.board[idx, ] == self.symbol):
                await self.channel.send(f'{self.active_player} hat Gewonnen!')
                self.reset()
                return

            elif np.all(self.board[:, idx] == self.symbol):
                await self.channel.send(f'{self.active_player} hat Gewonnen!')
                self.reset()
                return

        if np.all(np.diagonal(self.board) == self.symbol):
            await self.channel.send(f'{self.active_player} hat Gewonnen!')
            self.reset()
            return

        elif np.all(type(self.board) == str):
            await self.channel.send('Unentschieden')
            self.reset()
            return
