from discord.ext import commands
import discord


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # sending message "!hey" triggers this function
    @commands.command()
    async def hey(self, ctx):
        """Test bot ping"""
        await ctx.send("HEY!!")


def setup(bot):
    bot.add_cog(Core(bot))
