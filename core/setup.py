import logging

import discord

from core import embeds
from core.utils import get_role


# TODO: Gastrolle auswählbar

async def setup_dialog(bot, member):
    await member.send(embed=embeds.setup_start)

    # loop until User tiped in a valid name
    while True:
        name = await bot.userinput(member.dm_channel, member)
        if len(name) < 32:
            break
        else:
            await member.send(embed=embeds.setup_name_error)

    # change Users Nickname to tiped name
    try:
        await member.edit(nick=name)
    except discord.Forbidden:
        logging.info(f'could not asign new nickname to member "{member.name}"')

    await member.send(embed=embeds.setup_group_select(name, bot.semesters))

    # loop until User tiped in a valid study_group_name
    flag = True
    roles_to_add = [bot.roles['student']]
    while flag:
        message = await bot.userinput(member.dm_channel, member)
        for group in bot.study_groups:
            if message.upper() == group.name:
                roles_to_add.append(group.role)
                await member.send(embed=embeds.setup_end(group.name))
                flag = False
                break
        else:
            await member.send(embed=embeds.setup_group_error(message))

    # Check if User already has study_group_name roles, if so, remove them
    for role in member.roles:
        if role in [group.role for group in bot.study_groups]:
            await member.remove_roles(role)

    await member.add_roles(*roles_to_add)
