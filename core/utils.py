import asyncio

from discord.ext import commands


def check_pinned(message):
    return not message.pinned


def is_admin():
    async def predicate(context):
        try:
            return context.author.guild_permissions.administrator
        except AttributeError:
            return False

    return commands.check(predicate)


async def send_more(messageable, content):
    # TODO: bisschen ausgeklügelteren algorithmus implementieren
    while True:
        if len(content) > 1995:
            await messageable.send(codeblock(content[:1994]))
            content = content[1994:]
        else:
            await messageable.send(codeblock(content))
            return


def codeblock(string):
    return f'```{string}```'


def ongoing_tasks():
    """Debugging helper function to print the number of running asyncio tasks."""
    print(len(asyncio.all_tasks()))


class UserInputEvent:
    def __init__(self, bot, channel, user):
        self.bot = bot
        self.channel = channel
        self.user = user
        self.queue = asyncio.Queue()

        self.bot.add_listener(self.on_message)

    @classmethod
    async def create(cls, bot, channel, user):
        event = cls(bot, channel, user)
        while True:
            return await event.queue.get()

    async def on_message(self, message):
        if message.author.id == self.user.id and message.channel == self.channel:
            await self.queue.put(message)

    def __del__(self):
        self.bot.remove_listener(self.on_message)
