from discord.ext import commands
from modules.EIT.utils import get_role


class Roles(commands.Cog):
    def __init__(self, eit):
        self.eit = eit

    @commands.command(name='gamer')
    async def gamer(self, context):
        """Zur Anzeige der Spielbereitschaft"""
        await self.toggle_role(context, self.eit.game_role)

    async def toggle_role(self, ctx, role_id):
        gamer_role = get_role(self.eit.guild, role_id)
        if gamer_role in ctx.author.roles:
            await ctx.author.remove_roles(gamer_role)
            await ctx.channel.send('Du gehörst jetzt zu den Gamern!')
        else:
            await ctx.author.add_roles(gamer_role)
            await ctx.channel.send('Du gehörst jetzt nicht mehr zu den Gamern!')