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
        ], autoreload=False)

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

        self.is_started = False

        self._buttons_changed = False
        self._is_stopped = False

        if not self.imageserver.is_running:
            self.imageserver.start()

        try:
            self.session_id, self.datapath, self.base_url = self.imageserver.new_session(self)
        except MaxSessionCountError:
            raise

    def __del__(self):
        self.imageserver.delete_session(self.session_id)

    async def start(self):
        """Starts the interactive Embed and sends the initial Embed.
           If it´s already startet or stopped, this call will be silently ignored."""

        if self._is_stopped or self.is_started:
            return

        self.message = await self.channel.send(embed=self.embed)

        for button in self.buttons:
            await button._add()

        self.is_started = True

    async def stop(self):
        """Stops the InteractiveEmbed and deletes the Message and Embed.
           After this is called, the InteractiveEmbed can´t be started again and should be discarded."""

        if self._is_stopped:
            return

        # TODO: if message is already deleted?
        await self.message.delete()
        self.imageserver.delete_session(self.session_id)

        self._is_stopped = True
        self.is_started = False

    async def update_message(self):
        """Updates the Message`s Embed.
           This needs to be called to commit the changes made to the Embed to the actual Message.
           If the InteractiveEmbed has not been startet yet or has been stopped, this call will be silently ignored."""

        if self.is_started:
            # TODO: if message has been deleted?
            # update embed
            await self.message.edit(embed=self.embed)

            # update buttons
            if self._buttons_changed:
                await self.message.clear_reactions()
                for button in self.buttons:
                    await button._add()
                self._buttons_changed = False

    def set_image(self, filename: str = None):
        """Sets the specified file as new Embed Image.
           This file has to be loaded through load_image() before. Otherwise this will raise a FileNotFoundError.
           The filename parameter can be omitted to remove the current image from the Embed."""

        if filename is None:
            self.embed.set_image(url=discord.Embed.Empty)
            return

        if os.path.isfile(self.datapath + '/' + filename):
            self.embed.set_image(url=self.base_url + filename)
        else:
            raise FileNotFoundError(f'{filename} does not exist in session directory, '
                                    f'probably because it has not been loaded before.')

    def load_image(self, filepath: Union[str, os.PathLike], filename: str = None):
        if filename is None:
            filename = os.path.basename(filepath)
        shutil.copyfile(filepath, str(self.datapath + '/' + filename))

    def remove_image(self):
        """Removes the current image from the Embed.
           Alias for set_image() with omitted filename parameter."""

        self.set_image()

    def set_title(self, title: str):
        """Sets the title of the Embed according to the title parameter."""

        self.embed.title = title

    def remove_title(self):
        """Removes the Embed´s title"""

        self.embed.title = ""

    def set_text(self, text: str):
        """Sets the description of the Embed according to the text parameter."""

        self.embed.description = text

    def remove_text(self):
        """Removes the Embed´s description"""

        self.embed.description = ""

    def add_button(self, emoji, callback: Callable = None, args: tuple = (), position: int = None):
        # TODO: If the emoji is already used as button?
        new_button = Button(self, emoji, callback, args)

        if position is None:
            self.buttons.append(new_button)
        else:
            self.buttons.insert(position, new_button)

        self._buttons_changed = True

        return new_button

    def remove_button(self, position):
        try:
            button = self.buttons.pop(position)
            button.delete()
            self._buttons_changed = True
        except IndexError:
            raise

    def clear_buttons(self):
        self.buttons = []
        self._buttons_changed = True


class Button:
    def __init__(self, interactive_embed, emoji, callback, args):
        self.emoji = emoji
        self.callback = callback
        self.args = args

        self.interactive_embed = interactive_embed

        self.is_active = False

    async def _add(self):
        await self.interactive_embed.message.add_reaction(self.emoji)

        # TODO: listener should be added by InteractiveEmbed not Button, unwanted reactions have to be cleared
        @self.interactive_embed.bot.listen('on_reaction_add')
        async def on_button_press(reaction, member):
            # only react to this button
            if reaction.message == self.interactive_embed.message and reaction.emoji == self.emoji:
                # ignore own reactions
                if member.id == self.interactive_embed.bot.user.id:
                    return

                # execute callback
                if asyncio.iscoroutinefunction(self.callback):
                    await self.callback(self, member, *self.args)
                elif callable(self.callback):
                    self.callback(self, member, *self.args)

                # clear reaction after callback execution,
                # this prevents calling the callback again, before the previous execution has finished
                try:
                    await self.interactive_embed.message.remove_reaction(reaction.emoji, member)
                except discord.NotFound:
                    pass

    async def delete(self):
        try:
            self.interactive_embed.buttons.remove(self)
        except ValueError:
            pass


class MaxSessionCountError(Exception):
    pass
