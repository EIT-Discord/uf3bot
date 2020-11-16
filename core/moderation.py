from discord.ext import commands


class ModTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        if ctx.prefix == self.bot.admin_prefix:
            try:
                if ctx.author.guild_permissions.manage_messages:
                    return True
            except AttributeError:
                pass
        return False

    @commands.group()
    async def clean(self, context, *amount: int):
        def check(msg):
            if msg.author == self.bot.user:
                
