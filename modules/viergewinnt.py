import asyncio

from discord.ext import commands

from core.interbed import InteractiveEmbed, ImageServer


def setup(bot):
    bot.add_cog(VierGewinnt(bot))


class VierGewinnt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.datapath = self.bot.datapath / 'viergewinnt'

    async def cb(self, member):
        await asyncio.sleep(5)
        print(self.datapath)
        print(member)

    @commands.command()
    async def start(self, context):
        imageserver = ImageServer(self.bot.datapath/'InteractiveEmbed', 'sers-mahlzeit.de')

        def test(member):
            print(member)

        interbed = InteractiveEmbed(self.bot, imageserver, context.channel)
        interbed.add_button(self.bot.guild.emojis[0], callback=test)

        await interbed.start()

        #await interbed.stop()
