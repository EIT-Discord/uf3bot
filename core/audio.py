import asyncio
import discord


class VoiceHandler:
    def __init__(self, bot):
        self.bot = bot
        self.vc = None

    async def play(self, member, stream):
        try:
            channel = member.voice.channel
        except AttributeError:
            return

        source = await discord.FFmpegOpusAudio.from_probe(stream, method='fallback')

        try:
            self.vc = await channel.connect()
        except discord.ClientException:
            self.vc.stop()
            await self.vc.move_to(channel)

        try:
            self.vc.play(source)
        except discord.ClientException:
            return

        try:
            while self.vc.is_playing():
                await asyncio.sleep(0.1)
            await self.vc.disconnect()
        except AttributeError:
            pass

    async def disconnect(self):
        if self.vc:
            await self.vc.disconnect()
