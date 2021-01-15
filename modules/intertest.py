from discord.ext import commands

from core.interbed import InteractiveEmbed, ImageServer


def setup(bot):
    bot.add_cog(InterTest(bot))


class InterSession:
    def __init__(self, bot, imageserver, datapath, channel):
        self.counter = 1
        self.range = (1, 5)

        self.datapath = datapath

        self.interbed = InteractiveEmbed(bot, imageserver, channel)

        self.interbed.add_button('⬆', callback=self.btn_up)
        self.interbed.add_button('⬇', callback=self.btn_down)

        for i in range(self.range[0], self.range[1]+1):
            self.interbed.load_image(self.datapath/f'{i}.jpg')

        self.interbed.set_image(f'{self.counter}.jpg')

    async def start(self):
        await self.interbed.start()

    async def btn_up(self, member):
        if self.counter >= self.range[1]:
            self.counter = self.range[0]
        else:
            self.counter += 1

        self.interbed.set_image(f'{self.counter}.jpg')
        await self.interbed.update_msg()

    async def btn_down(self, member):
        if self.counter <= self.range[0]:
            self.counter = self.range[1]
        else:
            self.counter -= 1

        self.interbed.set_image(f'{self.counter}.jpg')
        await self.interbed.update_msg()


class InterTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.datapath = self.bot.datapath / 'viergewinnt'

        self.imageserver = ImageServer(self.bot.datapath/'InteractiveEmbed', 'sers-mahlzeit.de')
        self.sessions = []

    @commands.command()
    async def start(self, context):
        ie = InterSession(self.bot, self.imageserver, self.datapath, context.channel)
        self.sessions.append(ie)
        await ie.start()

    @commands.command()
    async def kot(self, context):
        interbed = InteractiveEmbed(self.bot, self.imageserver, context.channel)
        interbed.load_image(self.datapath/'test.png')
        interbed.set_image('test.png')
        await interbed.start()
