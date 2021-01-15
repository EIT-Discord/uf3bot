import asyncio
import os
import shutil
from threading import Thread
from typing import Union, Callable

import discord
from tornado import web, ioloop
from discord import TextChannel, Embed


class ImageServer:
    def __init__(self, datapath: Union[str, os.PathLike], ip: str, port: int = 8000):
        self.datapath = str(datapath)
        self.ip = ip
        self.port = port
        self.tornado_loop = None

        self.sessions = {}
        self.is_running = False

    def start(self):
        self.is_running = True
        thread = Thread(target=self.tornado_start, daemon=True)
        thread.start()

    async def stop(self):
        self.tornado_loop.stop()
        self.is_running = False

    def tornado_start(self):
        # TODO: works for now, but needs a closer look into the tornado documentation
        asyncio.set_event_loop(asyncio.new_event_loop())
        application = web.Application([
            (r"/(.*)", web.StaticFileHandler, {"path": str(self.datapath)})
        ], debug=True, autoreload=False)

        self.tornado_loop = ioloop.IOLoop.current()
        httpserver = application.listen(self.port)
        self.tornado_loop.start()
        print('loop stopped')
        httpserver.stop()
        print('port closed')

    def new_session(self, interactive_embed):
        try:
            session_id = self.generate_session_id()
        except MaxSessionCountError:
            raise

        session_path = str(self.datapath) + '/' + str(session_id)
        base_url = f'http://{self.ip}:{self.port}/{session_id}/'

        try:
            os.mkdir(session_path)
        except FileExistsError:
            shutil.rmtree(session_path)
            os.mkdir(session_path)

        self.sessions[session_id] = interactive_embed

        return session_id, session_path, base_url

    def delete_session(self, session_id):
        self.sessions.pop(session_id)
        shutil.rmtree(self.datapath + '/' + str(session_id))

    def generate_session_id(self):
        for i in range(5):
            if i not in self.sessions:
                return i
        else:
            raise MaxSessionCountError


class InteractiveEmbed:
    def __init__(self, bot, imageserver: ImageServer, channel: TextChannel):
        self.bot = bot
        self.imageserver = imageserver
        self.channel = channel

        self.embed = Embed()
        self.message = None
        self.buttons = []

        if not self.imageserver.is_running:
            self.imageserver.start()

        try:
            self.session_id, self.datapath, self.base_url = self.imageserver.new_session(self)
        except MaxSessionCountError:
            raise

    async def start(self):
        self.message = await self.channel.send(embed=self.embed)
        for button in self.buttons:
            await button.add()

    async def stop(self):
        await self.message.delete()
        self.imageserver.delete_session(self.session_id)

    async def update_msg(self):
        await self.message.edit(embed=self.embed)
        # TODO: wenn die nachricht gelöscht wird?

    def set_image(self, filename: str):
        if os.path.isfile(self.datapath + '/' + filename):
            self.embed.set_image(url=self.base_url + filename)
        else:
            raise FileNotFoundError(f'{filename} does not exist in session directory, '
                                    f'probably because it has not been loaded before.')

    def load_image(self, filepath: Union[str, os.PathLike], filename: str = None):
        if filename is None:
            filename = os.path.basename(filepath)
        shutil.copyfile(filepath, str(self.datapath + '/' + filename))

    def set_title(self, title: str):
        self.embed.title = title

    def set_text(self, text: str):
        self.embed.description = text

    def add_button(self, emoji: discord.Emoji, callback: Callable = None, args: tuple = ()):
        button = Button(self, emoji, callback, args)
        self.buttons.append(button)
        return button

    def remove_button(self):
        raise NotImplementedError

    def clear_buttons(self):
        raise NotImplementedError

    def remove_text(self):
        raise NotImplementedError

    def remove_title(self):
        raise NotImplementedError

    def remove_image(self):
        raise NotImplementedError

class Button:
    def __init__(self, interbed, emoji, callback, args):
        self.interbed = interbed
        self.emoji = emoji
        self.callback = callback
        self.args = args

    async def add(self):
        await self.interbed.message.add_reaction(self.emoji)

        @self.interbed.bot.listen('on_reaction_add')
        async def on_reaction(reaction, member):
            # ignore own reactions
            if member.id == self.interbed.bot.user.id:
                return

            # clear all other reactions immediately
            try:
                await self.interbed.message.remove_reaction(reaction.emoji, member)
            except discord.NotFound:
                pass

            # call callback
            if reaction.emoji == self.emoji:
                if asyncio.iscoroutinefunction(self.callback):
                    await self.callback(member, *self.args)
                elif callable(self.callback):
                    self.callback(member, *self.args)


class MaxSessionCountError(Exception):
    pass
