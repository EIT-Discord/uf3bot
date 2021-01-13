from discord.ext import commands

from core.utils import codeblock


def setup(bot):
    bot.add_cog(Stats(bot))


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command("stats")
    async def calcstats(self, context):
        async with context.channel.typing():
            await context.channel.send(codeblock('fetching messages...'))

            messages = await fetch_messages(context.guild)

            await context.channel.send(codeblock(f'retrieved {len(messages)} messages.'))
            await context.channel.send(codeblock('evaluating...'))

            result = analize(messages)

            for dict in result:
                try:
                    name_dict = {}
                    for key, val in dict.items():
                        name_dict[key.name] = val
                except AttributeError:
                    name_dict = dict

                sorted_result = [(w, name_dict[w]) for w in sorted(name_dict, key=name_dict.get, reverse=True)]
                await context.channel.send(str(sorted_result))

            return
            authors_output = 'Most frequent authors:\n'
            for idx, val in enumerate(authors_result):
                authors_output += f'{idx + 1}. {val[0]}  ({val[1]})\n'
                if idx > 20:
                    break

            await context.channel.send(codeblock(authors_output))

            words_output = 'Most used words:\n'
            for idx, val in enumerate(words_result):
                words_output += f'{idx + 1}. {val[0]}  ({val[1]})\n'
                if idx > 20:
                    break

            await context.channel.send(codeblock(words_output))


async def fetch_messages(guild):
    messages = []
    for channel in guild.text_channels:
        async for message in channel.history(limit=20000):
            if not message.author.bot:
                messages.append(message)

    return messages


def analize(messages):

    authorcount = {}    # How many messages an author sent
    mentioned = {}      # How often a user got mentioned
    mentions = {}       # How often a user mentioned somebody
    reactionused = {}   # How often a reaction was used
    reactioncount = {}  # How much reactions were on a message

    for message in messages:
        author = message.author

        # authorcount
        if author in authorcount:
            authorcount[author] += 1
        else:
            authorcount[author] = 1

        # mentioned
        for member in message.mentions:
            if member in mentioned:
                mentioned[member] += 1
            else:
                mentioned[member] = 1

        # mentions
        if message.mentions:
            if author in mentions:
                mentions[author] += 1
            else:
                mentions[author] = 1

        # reactionused
        for reaction in message.reactions:
            if reaction.emoji in reactionused:
                reactionused[reaction.emoji] += reaction.count
            else:
                reactionused[reaction.emoji] = reaction.count

        # reactioncount
        if message.reactions:
            reactioncount[message] = 0
            for reaction in message.reactions:
                reactioncount[message] += reaction.count

        get_words(message.content)

    return authorcount, mentioned, mentions, reactionused, reactioncount


def get_words(content):
    words = []
    for raw_word in content.split(' '):
        word = raw_word.strip('*_~`"!?.,;/()=&%')

        if not word.isalpha():
            continue

    return words
