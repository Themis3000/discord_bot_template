from discord.ext import commands
import discord
from collections import deque
import youtube_dl
from youtube_search import YoutubeSearch
from utils.emoji import from_numbers
from utils.bot import BotUtils

queues = {}


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel"""
        voicestate = ctx.author.voice
        if voicestate is not None:
            if ctx.voice_client is not None:
                if ctx.voice_client.channel != voicestate.channel:
                    return await ctx.voice_client.move_to(voicestate.channel)
            else:
                await voicestate.channel.connect()
                queues[ctx.guild.id] = Queue()
        else:
            await ctx.send("You must be in a voice channel")

    @commands.command()
    async def play(self, ctx):
        """Plays a song from youtube"""
        search = ctx.message.content[len(ctx.command.name) + 2:]
        message = await ctx.send(f"Searching for `{search}`:mag:")
        results = YoutubeSearch(search, max_results=4).to_dict()
        lookup_message = f"Search results for ***{search}***:\n"
        for i, result in enumerate(results):
            lookup_message += f"{from_numbers(i + 1)} `[{result['duration']}]` ***{result['title']}***\n"
        await message.edit(content=lookup_message)
        reaction, sender = await BotUtils.numbered_reaction_menu(self.bot, message, len(results), ctx.author)
        if reaction is not None:
            song_data = results[reaction-1]
            song = Song(f"https://www.youtube.com{song_data['url_suffix']}",
                        song_data["title"],
                        song_data["duration"],
                        ctx.author)
            if ctx.guild.id not in queues:
                queues[ctx.guild.id] = Queue()
            queues[ctx.guild.id].add_song(song)
            await message.edit(content=f":white_check_mark: Added ***{song.name}***")

    @commands.command()
    async def queue(self, ctx):
        """Displays the server's song queue"""
        queue = queues[ctx.guild.id]
        message_text = "Song queue:\n"
        for i, song in enumerate(queue.songs):
            message_text += f"{i+1}. `{song.duration}` {song.name}\n"
        await ctx.send(message_text)

    @commands.command()
    async def stop(self, ctx):
        """disconnects from current voice channel"""
        await ctx.voice_client.disconnect()
        del queues[ctx.guild.id]


class Queue:
    def __init__(self):
        self.songs = deque()
        self.playing = False
        self.current_song = None

    def pop_left(self):
        return self.songs.popleft()

    def add_song(self, song):
        self.songs.append(song)

    def __len__(self):
        self.songs.__len__()


class Song:
    def __init__(self, url, name, duration, adder=None, preload=False):
        self.url = url
        self.name = name
        self.duration = duration
        self.adder = adder
        self.data = None
        if preload:
            self.load_song()

    def load_song(self):
        self.data = None


def setup(bot):
    bot.add_cog(Music(bot))
