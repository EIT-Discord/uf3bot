import asyncio

from discord.ext import commands

from core.embedinteraction import InteractiveEmbed


def setup(bot):
    bot.add_cog(VierGewinnt(bot))


class VierGewinnt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.datapath = self.bot.datapath / 'viergewinnt'

    @commands.command()
    async def start(self, context):
        ie = InteractiveEmbed(self.bot, context.channel)
        await ie.start()

        for i in range(1, 6):
            ie.load_image(self.datapath / f'{i}.jpg', f'{i}.jpg')
        for i in range(1, 6):
            ie.set_image(f'{i}.jpg')
            await asyncio.sleep(2)
            await ie.update_msg()

        await ie.stop()
