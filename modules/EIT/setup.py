import discord

from core.utils import UserInputEvent
from modules.EIT import embeds
from modules.EIT.utils import get_study_groups, get_role


# TODO: Gastrolle auswählbar

async def setup_dialog(eit, member):
    # send beginning message
    await member.send(embed=embeds.setup_start())

    # loop until User tiped in a valid name
    while True:
        # Wait for User input
        message = await UserInputEvent.create(eit.bot, member.dm_channel, member)
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
    await member.send(embed=embeds.setup_group_select(name, eit))

    flag = True

    # loop until User tiped in a valid study_group_name
    while flag:
        message = await UserInputEvent.create(eit.bot, member.dm_channel, member)

        # Check if User tiped in a valid study_group_name
        for study_group in get_study_groups(eit):
            if message.content.upper() == study_group['name']:
                # break loop if input is a valid study_group_name
                flag = False
                break
        else:
            await member.send(embed=embeds.setup_group_error(message))

    # On successful study_group_name selection, give User the student role
    await member.add_roles(get_role(eit.guild, eit.student_role_id))

    # Check if User already has study_group_name roles, if so, remove them
    for role in member.roles:
        if role in [get_role(eit.guild, x['id']) for x in get_study_groups(eit)]:
            await member.remove_roles(role)

    # set members study_group_name according to chosen study_group_name
    try:
        await member.add_roles(get_role(eit.guild, study_group['id']))
    except NameError:
        print(f'Something went wrong in setup of User "{member.name}".\n Aborting setup')
        return

    await member.send(embed=embeds.setup_end(study_group['name']))
