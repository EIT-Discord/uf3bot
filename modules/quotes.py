import random

from discord.ext import commands


def setup(bot):
    bot.add_cog(QuoteBot(bot))


class QuoteBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quotes = []
        self.quotepath = self.bot.datapath/'quotes.txt'
        self.load()

    def load(self):
        try:
            with self.quotepath.open('r') as file:
                for line in file.readlines():
                    if line != '\n':
                        self.quotes.append(line[:-1])
        except FileNotFoundError:
            print('no quotes found')

    @commands.command()
    async def rq(self, context):
        try:
            quote = random.choice(self.quotes)
            await context.channel.send(quote)
        except IndexError:
            await context.channel.send(f'_"Moe123 komm doch bitte herbei"_ ~ {context.author.name}')

    @commands.command()
    async def addq(self, context, *, quote: str):
        self.quotes.append(quote)
        await context.channel.send(f'_Added quote: \n{quote}_')
        self.save()

    def save(self):
        with self.quotepath.open('w+') as file:
            file.truncate(0)
            for quote in self.quotes:
                file.write(quote + '\n')
