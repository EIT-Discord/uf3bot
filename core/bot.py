import logging
import asyncio

import discord
from discord.ext import tasks
from discord.ext.commands import bot

from core.commands import Commands
from core.models import StudyGroup, Semester
from core.setup import setup_dialog


class UfffBot(bot.Bot):
    def __init__(self, command_prefix, config, datapath, **kwargs):
        super().__init__(command_prefix, **kwargs)

        self.config = config
        self.datapath = datapath

        self.app_id = None

        self.command_prefix = '!'
        self.presence = ''

        self.guild = None
        self.roles = {}
        self.channels = {}
        self.semesters = []
        self.study_groups = []

    async def on_ready(self):
        self.app_id = (await self.application_info()).id

        print("-------------------------")
        print('Logged in as:')
        print(f"{str(self.user)}, {self.user.id}")
        print("-------------------------")
        print("Use this URL to invite the bot to your server:")
        print(f'https://discordapp.com/oauth2/authorize?client_id={self.app_id}&scope=bot')
        print("-------------------------")

        self.parse_config()

        self.add_cog(Commands(self))
        self.tasks.start()
        await self.change_presence(status=discord.Status.online, activity=discord.Game(self.presence))

    async def on_member_join(self, member):
        """When a new member joins the server, call the setup-dialog on him."""
        await setup_dialog(self, member)

    async def userinput(self, channel, member):
        queue = asyncio.Queue()

        async def on_message(message):
            if message.author.id == member.id and message.channel == channel:
                await queue.put(message)

        self.add_listener(on_message)
        answer = await queue.get()
        self.remove_listener(on_message)
        return answer.content

    @tasks.loop(seconds=30)
    async def tasks(self):
        """Periodically logs the number of running asyncio tasks."""
        task_count = len(asyncio.all_tasks())
        logging.debug(f'{task_count} asyncio tasks currently running.')

    def parse_config(self):
        # get guild from config
        for guild in self.guilds:
            if self.config['server']['id'] == guild.id:
                self.guild = guild
                break
        else:
            logging.warning('The bot is not a member of the guild with the specified guild id')

        self.command_prefix = self.config['bot']['prefix']
        self.presence = self.config['bot']['presence']

        # get roles from config
        for role_name, role_id in self.config['server']['roles'].items():
            role = discord.utils.get(self.guild.roles, id=role_id)
            if role:
                self.roles.update({role_name: role})
            else:
                logging.warning(f'role "{role_name}" not found in guild "{self.guild.name}"')

        # get channels from config
        for channel_name, channel_id in self.config['server']['channels'].items():
            channel = discord.utils.get(self.guild.channels, id=channel_id)
            if channel:
                self.channels.update({channel_name: channel})
            else:
                logging.warning(f'channel "{channel_name}" not found in guild "{self.guild.name}"')

        # get semesters from config
        for sem_year, semester in self.config['server']['semesters'].items():
            new_semester = Semester(sem_year)

            sem_channel = discord.utils.get(self.guild.channels, id=semester['channel'])
            if sem_channel:
                new_semester.channel = sem_channel
            else:
                logging.warning(f'channel of {new_semester} not found in guild "{self.guild}"')

            for gr_name, gr_id in semester['groups'].items():
                gr_role = discord.utils.get(self.guild.roles, id=gr_id)
                if gr_role:
                    new_group = StudyGroup(gr_name, gr_role, new_semester)
                    new_semester.groups.append(new_group)
                    self.study_groups.append(new_group)
                else:
                    logging.warning(f'role "{gr_name}" not found in guild "{self.guild}"')

            self.semesters.append(new_semester)
