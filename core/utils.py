import discord
from discord.ext import commands


def is_admin():
    """Checks if the member who invoked the command has administrator permissions on this server"""
    async def predicate(context):
        try:
            return context.author.guild_permissions.administrator
        except AttributeError:
            return False
    return commands.check(predicate)


async def send_more(messageable, content):
    """Takes a string and sends it as multiple messages if
    needed to bypass the discord limit of 2000 chars per message."""
    # TODO: ausgeklügelteren algorithmus implementieren
    while True:
        if len(content) > 1995:
            await messageable.send(codeblock(content[:1994]))
            content = content[1994:]
        else:
            await messageable.send(codeblock(content))
            return


def codeblock(string):
    """Wraps a string into a codeblock"""
    return f'```{string}```'


def get_member(bot, user):
    return discord.utils.get(bot.guild.members, id=user.id)
