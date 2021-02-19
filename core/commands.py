import discord
from discord.ext import commands

from core.setup import setup_dialog
from core.utils import is_admin, get_member


async def toggle_role(member, role):
    if role in member.roles:
        await member.remove_roles(role)
        await member.send(f'Du hast die Rolle **{role.name}** erhalten!')
    else:
        await member.add_roles(role)
        await member.send(f'Deine Rolle **{role.name}** wurde entfernt!')


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @is_admin()
    @commands.command()
    async def presence(self, context, *, presence: str):
        """Set the bots discord presence"""
        await self.bot.set_presence(presence)
        await context.channel.send(f"_Presence set to {presence}._")

    @commands.command()
    async def echo(self, context):
        a = await self.bot.userinput(context.channel, context.author)
        await context.channel.send(a)

    @is_admin()
    @commands.command()
    async def clean(self, context):
        """Deletes up to 10k unpinned messages in this channel"""
        await context.channel.send('Möchtest du wirklich alle Nachrichten in diesem Channel löschen?')
        message = await self.bot.userinput(context.channel, context.author)
        if message.content.lower() in ['ja', 'yes', 'y']:
            await context.channel.purge(check=lambda msg: not msg.pinned, limit=10000)

    @is_admin()
    @commands.command()
    async def clear(self, context, amount: int):
        """Delete the given amount of unpinned messages in this channel"""
        await context.channel.purge(check=lambda msg: not msg.pinned, limit=amount+1)

    @commands.command()
    async def gamer(self, context):
        """Erhalte/Entferne die Rolle Gamer"""
        member = get_member(self.bot, context.author)
        await toggle_role(member, self.bot.roles['gamer'])

    @commands.command()
    async def setup(self, context):
        """Startet den Setup-Dialog"""
        member = get_member(self.bot, context.author)
        await setup_dialog(self.bot, member)

    @commands.command()
    async def admin(self, context):
        embed = discord.Embed(name='Admins')
        admin_dict = {"Yannic": "Yannic Breiting (Der Grüne)",
                      "Elias": "Elias Deking (The Brain)",
                      "Franz": "Franz Ostler (Da Wirtshausfranz)",
                      "Martin": "Martin Kistler (The Nerd)",
                      "Benni": "Benni Draxlbauer (The Beachboy)",
                      "Michi": "Michi Besl (Der Feuerwehrmann)",
                      "Merih": "Merih Cetin (Der TUM-Student)",
                      "Jan": "Jan Duchscherer (The Brain aus der B)"}

        for admin_name, description in admin_dict.items():
            for emoji in self.bot.guild.emojis:
                if admin_name.lower() == emoji.name.lower():
                    embed.add_field(name=description, value=str(emoji), inline=False)
        await context.channel.send(embed=embed)
