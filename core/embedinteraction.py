import asyncio
import os
import shutil
from threading import Thread

from tornado import ioloop
from tornado import web
from discord import Embed


class InteractiveEmbed:
    def __init__(self, bot, channel):
        self.bot = bot

        self.channel = channel
        self.embed = Embed()
        self.message = None

        self.imageserver = bot.imageserver

        assert self.imageserver is not None

        if not self.imageserver.is_running:
            self.bot.imageserver.start()

        try:
            self.session_id, self.datapath, self.base_url = self.imageserver.new_session(self)
        except MaxSessionCountError:
            raise

    async def start(self):
        self.message = await self.channel.send(embed=self.embed)

    async def stop(self):
        await self.message.delete()
        self.imageserver.delete_session(self.session_id)

    async def update_msg(self):
        await self.message.edit(embed=self.embed)
        # TODO: wenn die nachricht gelöscht wird?

    def set_image(self, filename):
        if (self.datapath / filename).exists():
            self.embed.set_image(url=self.base_url + filename)
        else:
            raise FileNotFoundError

    def load_image(self, filepath, filename):
        shutil.copyfile(filepath, str(self.datapath / filename))


class ImageServer:
    def __init__(self, bot, ip, port=8000):
        self.datapath = bot.datapath / 'InteractiveEmbed'
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
            (r"/(.*)", web.StaticFileHandler, {"path": str(self.datapath)},),
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

        session_path = self.datapath / str(session_id)
        base_url = f'http://{self.ip}:{self.port}/{session_id}/'
        print(base_url)
        try:
            os.mkdir(session_path)
        except FileExistsError:
            shutil.rmtree(session_path)
            os.mkdir(session_path)

        self.sessions[session_id] = interactive_embed
        return session_id, session_path, base_url

    def delete_session(self, session_id):
        self.sessions.pop(session_id)
        shutil.rmtree(self.datapath/str(session_id))

    def generate_session_id(self):
        for i in range(5):
            if i not in self.sessions:
                return i
        else:
            raise MaxSessionCountError


class MaxSessionCountError(Exception):
    pass