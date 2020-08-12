"""
Core bot commands essential for built in features
"""
from discord.ext import commands
import discord


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Test bot ping"""
        await ctx.send(f"Pong! I am {str(self.bot.latency*1000)[:4]}ms latent to discord servers")


def setup(bot):
    bot.add_cog(Core(bot))
