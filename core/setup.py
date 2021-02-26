import logging

import discord

from core import embeds


def is_valid(name):
    """Checks if the typed in name is valid"""
    if len(name) > 32 or not all(x.isalpha() or x.isspace() for x in name):
        return False
    else:
        return True


async def setup_dialog(bot, member):
    await member.send(embed=embeds.setup_start)

    # loop until User tiped in a valid name
    while True:
        name = await bot.userinput(member.dm_channel, member)
        if is_valid(name):
            break
        else:
            await member.send(embed=embeds.setup_name_error)

    # change Users Nickname to tiped name
    try:
        await member.edit(nick=name)
    except discord.Forbidden:
        logging.info(f'could not asign new nickname to member "{member.name}"')

    await member.send(embed=embeds.setup_group_select(name, bot.semesters))

    # loop until User tiped in a valid studygroup
    flag = True
    roles_to_add = [bot.roles['student']]
    while flag:
        message = await bot.userinput(member.dm_channel, member)
        if message.upper() == 'GAST':
            roles_to_add.append(bot.roles['gast'])
            await member.send(embed=embeds.setup_end("Gast"))
            break

        for group in bot.study_groups:
            if message.upper() == group.name:
                roles_to_add.append(group.role)
                await member.send(embed=embeds.setup_end(group.name))
                flag = False
                break
        else:
            await member.send(embed=embeds.setup_group_error(message))

    # Check if User already has studygroup roles, if so, remove them
    for role in member.roles:
        if role == bot.roles['gast'] or role in [group.role for group in bot.study_groups]:
            await member.remove_roles(role)

    await member.add_roles(*roles_to_add)
