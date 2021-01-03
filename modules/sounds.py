import asyncio
import os
import random
<<<<<<< Updated upstream:modules/sounds.py

=======
import wave
import discord
import numpy as np
from matplotlib import pyplot as plt
>>>>>>> Stashed changes:modules/audio.py
from discord.ext import commands
import ffmpeg

from core.utils import send_more, is_admin


def setup(bot):
    bot.voice = VoiceHandler(bot)
    bot.add_cog(SoundBoard(bot))


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


class SoundBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.soundspath = self.bot.datapath/'MP3'
        self.temppath = self.bot.temppath

        self.soundfiles = {}

        self.sus_session = None
        self.listening_mode_active = False
        self.on_join_mode_active = False

        self.bot.add_listener(self.on_message)
        self.bot.add_listener(self.on_voice_state_update)

    def load_sounds(self):
        for sound in self.soundspath.iterdir():
            if sound.name.endswith('.mp3'):
                self.soundfiles.update({sound.name[:-4]: sound})

    async def play_sound(self, member, sound_name_in):
        self.load_sounds()
        for sound_name, sound_path in self.soundfiles.items():
            if sound_name.lower() == sound_name_in.lower():
                await self.bot.voice.play(member, sound_path)

    async def play_random_sound(self, member):
        sound_name = random.choice(list(self.soundfiles))
        await self.bot.voice.play(member, self.soundfiles[sound_name])

    @commands.command()
    async def play(self, context, *sound_name_in: str):
        if len(sound_name_in) == 0:
            await self.play_random_sound(context.author)
        else:
            await self.play_sound(context.author, sound_name_in[0])

    @commands.command(name='lm')
    @is_admin()
    async def listener_mode(self, context):
        self.listening_mode_active = not self.listening_mode_active

        if self.listening_mode_active:
            await context.channel.send(f'_Listening mode enabled_')
        else:
            await context.channel.send(f'_Listening mode disabled_')

    @commands.command(name='oj')
    @is_admin()
    async def on_join_mode(self, context):
        self.on_join_mode_active = not self.on_join_mode_active

        if self.on_join_mode_active:
            await context.channel.send(f'_On join enabled_')
        else:
            await context.channel.send(f'_On join disabled_')

    @commands.command()
    async def stop(self, context):
        if self.bot.voice.vc:
            await self.bot.voice.disconnect()

    @commands.command()
    async def list(self, context):
        self.load_sounds()
        out = ''
        for sound_name in self.soundfiles:
            out += '\n' + sound_name
        await send_more(context.channel, out)

    @commands.group()
    async def sus(self, context):
        print(self.sus_session)

    @sus.command()
    async def load(self, context, filename: str):
        try:
            file = self.get_filepath(filename)
        except FileNotFoundError:
            await context.send('_File not found_')
            return

        temp_wav_path = str(self.bot.temppath / 'ffmpg_conv.wav')

        try:
            os.remove(temp_wav_path)
        except FileNotFoundError:
            pass

        stream = ffmpeg.input(str(file)).output(temp_wav_path)
        ffmpeg.run(stream)

        self.sus_session = PCMAudio.from_wav(temp_wav_path)

    @sus.command(name='spect')
    async def sus_spect(self, context):
        if not self.sus_session:
            return

        self.sus_session.plot_spect(str(self.bot.temppath/'spect.png'))

        with open(self.bot.temppath/'spect.png', 'rb') as file:
            await context.channel.send('', file=discord.File(file))

    @sus.command(name='play')
    async def sus_play(self, context):
        if not self.sus_session:
            return

        temp_wav_path = str(self.bot.temppath/'ffmpg_conv.wav')
        temp_mp3_path = str(self.bot.datapath/'MP3/ffmpg_conv.mp3')

        for file in [temp_mp3_path, temp_wav_path]:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass

        self.sus_session.to_wav(temp_wav_path)
        stream = ffmpeg.input(temp_wav_path).output(temp_mp3_path)
        ffmpeg.run(stream)
        self.load_sounds()
        await self.play_sound(context.author, 'ffmpg_conv')

    @sus.command('filter')
    async def sus_filter(self, context, filtertype: str, fgrenz: int):
        if not self.sus_session:
            return

        self.sus_session = self.sus_session.filter(filtertype, fgrenz)

    async def on_message(self, message):
        if not self.listening_mode_active or message.author == self.bot.user:
            return

        self.load_sounds()
        for sound_name, sound_path in self.soundfiles.items():
            if sound_name in message.content:
                await self.bot.voice.play(message.author, sound_path)

    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user or not self.on_join_mode_active:
            return
        if before.channel is None and after.channel:
            if after.channel == self.bot.guild.afk_channel:
                return
            await self.play_random_sound(member)
<<<<<<< Updated upstream:modules/sounds.py
=======

    def get_filepath(self, filename):
        self.load_sounds()
        if filename not in self.soundfiles:
            raise FileNotFoundError
        else:
            return self.soundfiles[filename]


class PCMAudio:
    def __init__(self, signal, samprate, sampwidth):
        self.sampwidth = sampwidth
        self.samprate = samprate

        self.signal = signal
        self.times = np.linspace(0, len(self), self.signal.size)

        self.spect = np.fft.rfft(self.signal)
        self.freq = np.fft.rfftfreq(len(self.signal))*self.samprate

    def __len__(self):
        return int(self.signal.size/self.samprate)

    def to_wav(self, filename: str):
        with wave.open(filename, mode='w') as file:
            file.setnchannels(1)
            file.setsampwidth(self.sampwidth)
            file.setframerate(self.samprate)
            file.setnframes(len(self.signal))
            file.setcomptype('NONE', 'not compressed')
            data = np.int16(self.signal).tobytes()
            file.writeframes(data)

    def filter(self, ftype, fgrenz):
        idx = (np.abs(self.freq - fgrenz)).argmin()     # the idx of the frequenzy nearest to fgrenz
        new_spect = self.spect.copy()
        if ftype == 'itp':
            new_spect[idx:] = 0
        elif ftype == 'ihp':
            new_spect[:idx] = 0
        else:
            print('Invalid filter type')
            return
        return PCMAudio(np.fft.irfft(new_spect), self.samprate, self.sampwidth)

    def plot_signal(self, temp_path):
        plt.plot(self.times, self.signal)
        plt.savefig(temp_path)
        plt.close()

    def plot_spect(self, temp_path):
        plt.plot(self.freq, np.fft.rfft(self.signal))
        plt.savefig(temp_path)
        plt.close()

    @classmethod
    def from_wav(cls, filename: str):
        with wave.open(filename) as file:
            params = file.getparams()
            raw_data = file.readframes(params.nframes)

        signal = cls._monotonize(raw_data, params.sampwidth, params.nchannels)
        return cls(signal, params.framerate, params.sampwidth)

    @staticmethod
    def _monotonize(raw_data, sampwidth, nchannels):
        dtype = np.dtype('Int' + str(8 * sampwidth))
        data = np.frombuffer(raw_data, dtype=dtype)
        return data[::nchannels]

>>>>>>> Stashed changes:modules/audio.py
