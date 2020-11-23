import discord


def is_student(eit, member):
    try:
        if eit.student_role_id in [role.id for role in member.roles]:
            return True
    except AttributeError:
        pass
    return False


def get_member(bot, user):
    return discord.utils.get(bot.guilds[0].members, id=user.id)


def get_study_groups(eit):
    """ Generator yielding all study_groups belonging to the guild"""

    for semester in eit.semester:
        for name, role_id in semester.study_groups.items():
            yield {'name': name, 'id': role_id}


def get_role(guild, role_id):
    return discord.utils.get(guild.roles, id=role_id)
