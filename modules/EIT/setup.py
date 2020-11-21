import discord
from discord.ext import commands

from core.utils import user_input
from modules.EIT import embeds
from modules.EIT.utils import get_study_groups, get_member, get_role


class StudentSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.eit = self.bot.eit
        self.guild = self.bot.guilds[0]
        self.bot.add_listener(self.on_member_join)

    async def cog_check(self, context):
        return True

    async def cog_after_invoke(self, context):
        pass

    async def on_member_join(self, member):
        await self.setup_dialog(member)

    @commands.command()
    async def setup(self, context):
        member = get_member(self.bot, context.author)
        await self.setup_dialog(member)

    async def setup_dialog(self, member):
        # send beginning message
        await member.send(embed=embeds.setup_start())

        # loop until User tiped in a valid name
        while True:
            # Wait for User input
            message = await user_input(self.bot, member.dm_channel, member)
            name = message.content

            # Check if User tiped in a valid name
            if len(name) < 32:
                break
            else:
                await member.send(embed=embeds.setup_name_error())

        # change Users Nickname to tiped in Name
        try:
            await member.edit(nick=name)
        except discord.Forbidden:
            pass

        # create group_selection embed
        await member.send(embed=embeds.setup_group_select(name, self.eit))

        flag = True

        # loop until User tiped in a valid study_group_name
        while flag:
            # Wait for user input
            message = await user_input(self.bot, member.dm_channel, member)

            # Check if User tiped in a valid study_group_name
            for study_group in get_study_groups(self.eit):
                if message.content.upper() == study_group['name']:
                    # break loop if input is a valid study_group_name
                    flag = False
                    break
            else:
                await member.send(embed=embeds.setup_group_error(message))

        # On successful study_group_name selection, give User the student role
        await member.add_roles(get_role(self.guild, self.eit.student_role_id))

        # Check if User already has study_group_name roles, if so, remove them
        for role in member.roles:
            if role in [get_role(self.guild, x['id']) for x in get_study_groups(self.eit)]:
                await member.remove_roles(role)

        # set members study_group_name according to chosen study_group_name
        try:
            await member.add_roles(get_role(self.guild, study_group['id']))
        except NameError:
            print(f'Something went wrong in setup of User "{member.name}".\n Aborting setup')
            return

        await member.send(embed=embeds.setup_end(study_group['name']))
