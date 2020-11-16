from discord.ext.commands import bot

from core.configuration import BotControl, get_config
from core.moderation import ModTools


class UffBot(bot.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(loop=None, *args, **kwargs)
        self.config = get_config()

    async def on_ready(self):
        print("-------------------------")
        print('Logged in as')
        print(f"{str(self.user)}, {self.user.id}")
        print("-------------------------")

        # load bot settings
        await self.config.load(self)
        self.add_cog(BotControl(self))
        self.add_cog(ModTools(self))
