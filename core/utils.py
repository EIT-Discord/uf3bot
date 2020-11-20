import asyncio
import discord


def is_admin(member):
    try:
        if member.guild_permissions.administrator:
            return True
    except AttributeError:
        pass
    return False
