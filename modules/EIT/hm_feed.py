import asyncio
import feedparser
import pickle

from discord.ext import tasks, commands


class HMFeed(commands.Cog):
    refresh_interval = 10

    def __init__(self, eit):
        self.entries = []
        self.picklepath = eit.bot.datapath/'hmfeed.pickle'
        self.url = eit.hm_feed_url
        self.channel = eit.hm_feed_channel

        self.load()
        self.refresh.start()

    @tasks.loop(seconds=refresh_interval)
    async def refresh(self):
        new_feed = feedparser.parse(self.url)
        new_entries = []
        for entry in new_feed["entries"]:
            new_entries.append(entry)

        new_entries.reverse()

        if new_entries == self.entries:
            return
        else:
            await self.compare_feeds(new_entries)
            self.save()

    def load(self):
        try:
            with self.picklepath.open('rb') as file:
                self.entries = pickle.load(file)
        except EOFError:
            pass
        except FileNotFoundError:
            pass

    def save(self):
        with self.picklepath.open('wb') as file:
            pickle.dump(self.entries, file)

    async def compare_feeds(self, new_entries):
        for entry in new_entries:
            if entry not in self.entries:
                await self.send_entry(entry)
        self.entries = new_entries

    async def send_entry(self, entry):
        message = await self.channel.send(entry['link'])
        asyncio.create_task(self.edit_embed(message, entry))

    @staticmethod
    async def edit_embed(message, entry, timeout=5):
        counter = 0

        while True:
            try:
                new_embed = message.embeds[0]

                new_embed.description = entry['summary']
                published = entry['published_parsed']
                str = f'Veröffentlicht am {published.tm_mday}.{published.tm_mon}.{published.tm_year}'
                new_embed.set_footer(text=str)
                await message.edit(content=None, embed=new_embed)
                return

            except IndexError or AttributeError:
                await asyncio.sleep(0.5)
                counter += 1

                if counter >= timeout * 2:
                    break
