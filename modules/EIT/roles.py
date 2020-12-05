from discord.ext import commands
from modules.EIT.utils import get_role


class Roles(commands.Cog):
    def __init__(self, eit):
        self.eit = eit

    @commands.command(name='gamer')
    async def gamer(self, context):
        """Erhalte/Entferne die Rolle Gamer"""
        await self.toggle_role(context, self.eit.game_role)

    async def toggle_role(self, ctx, role_id):
        gamer_role = get_role(self.eit.guild, role_id)
        if gamer_role in ctx.author.roles:
            await ctx.author.remove_roles(gamer_role)
            await ctx.author.send('Du hast die Rolle **Gamer** erhalten!')
        else:
            await ctx.author.add_roles(gamer_role)
            await ctx.author.send('Deine Rolle **Gamer** wurde entfernt!')
