from discord.ext import commands
import discord


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel"""
        voicestate = ctx.author.voice
        if voicestate is not None:
            if ctx.voice_client is not None:
                return await ctx.voice_client.move_to(voicestate.channel)
            else:
                await voicestate.channel.connect()
        else:
            await ctx.send("You must be in a voice channel")

    @commands.command()
    async def play(self, ctx, song):
        """Plays a song from youtube"""
        pass

    @commands.command()
    async def stop(self, ctx):
        """disconnects from current voice channel"""
        await ctx.voice_client.disconnect()


def setup(bot):
    bot.add_cog(Core(bot))
