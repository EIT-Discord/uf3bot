import asyncio
import discord


async def delete_messages(*messages, delay=5):
    await asyncio.sleep(delay)
    for message in messages:
        try:
            await message.delete()
        except discord.errors.Forbidden:
            pass
