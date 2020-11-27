from discord.ext import commands
from modules.EIT.utils import get_role, is_student


class Roles(commands.Cog):
    def __init__(self, eit):
        self.eit = eit

    async def cog_check(self, context):
        return is_student(self.eit, context.author)

    @commands.command(name='amongus')
    async def among_us(self, context):
        await self.toggle_role(context.author, self.eit.game_roles['among_us'])

    @commands.command()
    async def csgo(self, context):
        await self.toggle_role(context.author, self.eit.game_roles['csgo'])

    async def toggle_role(self, member, role_id):
        among_us_role = get_role(self.eit.guild, role_id)
        if among_us_role in member.roles:
            await member.remove_roles(among_us_role)
        else:
            await member.add_roles(among_us_role)
