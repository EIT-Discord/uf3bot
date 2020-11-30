import random

from discord.ext import commands

from core.audio import VoiceHandler
from core.utils import send_more, is_admin


def setup(bot):
    bot.voice = VoiceHandler(bot)
    bot.add_cog(SoundBoard(bot))


class SoundBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.soundspath = self.bot.datapath/'MP3'
        self.sounds = {}

        self.bot.add_listener(self.on_message)
        self.bot.add_listener(self.on_voice_state_update)
        self.listening_mode_active = False

    def load_sounds(self):
        for sound in self.soundspath.iterdir():
            if sound.name.endswith('.mp3'):
                self.sounds.update({sound.name[:-4]: sound})

    async def play_sound(self, member, sound_name_in):
        self.load_sounds()
        for sound_name, sound_path in self.sounds.items():
            if sound_name.lower() == sound_name_in.lower():
                await self.bot.voice.play(member, sound_path)

    async def play_random_sound(self, member):
        self.load_sounds()
        sound_name = random.choice(list(self.sounds))
        await self.bot.voice.play(member, self.sounds[sound_name])

    @commands.command()
    async def play(self, context, *sound_name_in: str):
        if len(sound_name_in) == 0:
            await self.play_random_sound(context.author)
        else:
            await self.play_sound(context.author, sound_name_in[0])

    @commands.command(name='lm')
    @is_admin()
    async def listener_mode(self, context):
        if self.listening_mode_active:
            self.listening_mode_active = False
            await context.channel.send(f'_Listening mode disabled_')
        else:
            self.listening_mode_active = True
            await context.channel.send(f'_Listening mode enabled_')

    @commands.command()
    async def stop(self, context):
        if self.bot.voice.vc:
            await self.bot.voice.disconnect()

    @commands.command()
    async def list(self, context):
        self.load_sounds()
        out = ''
        for sound_name in self.sounds:
            out += '\n' + sound_name
        await send_more(context.channel, out)

    async def on_message(self, message):
        if not self.listening_mode_active or message.author == self.bot.user:
            return

        self.load_sounds()
        for sound_name, sound_path in self.sounds.items():
            if sound_name in message.content:
                await self.bot.voice.play(message.author, sound_path)

    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user:
            return
        if before.channel is None and after.channel:
            if after.channel == self.bot.guild.afk_channel:
                return
            await self.play_random_sound(member)
