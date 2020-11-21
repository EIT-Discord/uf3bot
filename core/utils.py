import asyncio


def is_admin(member):
    try:
        if member.guild_permissions.administrator:
            return True
    except AttributeError:
        pass
    return False


async def user_input(bot, channel, user):
    event = UserInputEvent(bot, channel, user)
    while True:
        return await event.queue.get()


async def c_user_input(context):
    event = UserInputEvent(context.bot, context.channel, context.user)
    while True:
        return await event.queue.get()


class UserInputEvent:
    def __init__(self, bot, channel, user):
        self.bot = bot
        self.channel = channel
        self.user = user
        self.queue = asyncio.Queue()

        self.bot.add_listener(self.on_message)

    async def on_message(self, message):
        if message.author.id == self.user.id and message.channel == self.channel:
            await self.queue.put(message)

    def __del__(self):
        self.bot.remove_listener(self.on_message)
