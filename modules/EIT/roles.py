from discord.ext import commands
from modules.EIT.utils import get_role


class Roles(commands.Cog):
    def __init__(self, eit):
        self.eit = eit

    @commands.command(name='gamer')
    async def gamer(self, context):
        """Zur Anzeige der Spielbereitschaft"""
        await self.toggle_role(context.author, self.eit.game_role)

    async def toggle_role(self, member, role_id):
        gamer_role = get_role(self.eit.guild, role_id)
        if gamer_role in member.roles:
            await member.remove_roles(gamer_role)
        else:
            await member.add_roles(gamer_role)
