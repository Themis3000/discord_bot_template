from youtubesearchpython import VideosSearch, Playlist
from discord.ext import commands
import discord
from collections import deque

from utils.emoji import from_numbers
from utils.bot import BotUtils


class Song:
    """Signifies a single song"""
    def __init__(self, url, name, duration, adder=None, preload=False):
        self.url = url
        self.name = name
        self.duration = duration
        self.adder = adder
        self.data = None
        if preload:
            self.load_song()

    def load_song(self):
        """Loads the song into memory to avoid steaming cutouts (not implemented)"""
        self.data = None


class Queue:
    """Signifies a single queue"""
    def __init__(self):
        self.songs = deque()
        self.playing = False
        self.current_song = None

    def pop_left(self) -> Song:
        """Removes the next up song from the queue and also returns it"""
        return self.songs.popleft()

    def add_song(self, song: Song):
        """Adds a song to the end of the queue"""
        self.songs.append(song)

    def add_song_next(self, song: Song):
        """Adds a song to the front of the queue"""
        self.songs.appendleft(song)

    def __len__(self):
        """Gets the item length of the queue (as opposed to time length)"""
        self.songs.__len__()


def dict_to_song(search_dict: dict, author: discord.user) -> Song:
    """Converts the dictionary provided by youtubesearchpython to a Song object"""
    return Song(search_dict['link'],
                search_dict['title'],
                search_dict['duration'],
                author)


class Queues:
    def __init__(self):
        self.guilds = {}

    def __getitem__(self, guild_id: str) -> Queue:
        """Gets the queue for a given guild. If none exists, one if created"""
        if guild_id not in self.guilds:
            self.guilds[guild_id] = Queue()
        return self.guilds[guild_id]

    def remove_queue(self, guild_id: str):
        """Removes a given guild's queue"""
        del self.guilds[guild_id]


queues = Queues()


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel"""
        voicestate = ctx.author.voice
        # if the sender is in a voice channel
        if voicestate is not None:
            # if the bot is in a voice channel
            if ctx.voice_client is not None:
                # if the bot is not in the same voice channel as the user
                if ctx.voice_client.channel != voicestate.channel:
                    return await ctx.voice_client.move_to(voicestate.channel)
            else:
                await voicestate.channel.connect()
        else:
            await ctx.send("You must be in a voice channel")

    @staticmethod
    async def searching_message(ctx: discord.ext.commands.Context, query: str) -> discord.Message:
        """Sends the universally used discord message specifying that the bot is searching"""
        return await ctx.send(f"Searching for `{query}`:mag:")

    @staticmethod
    async def add_to_queue_message(message: discord.Message, song_name: str) -> discord.Message:
        """Edits a discord message to the one used universally specifying that a song was added to the queue"""
        return await message.edit(content=f":white_check_mark: Added `{song_name}` to the queue")

    @staticmethod
    def add_to_queue(guildId, song, add_to_start=False):
        """Adds a song to a given guild's queue"""
        if add_to_start:
            queues[guildId].add_song_next(song)
            return
        queues[guildId].add_song(song)

    @staticmethod
    def get_query(ctx: discord.ext.commands.Context) -> str:
        return ctx.message.content[len(ctx.invoked_with) + 2:]

    @commands.command(aliases=["nextsearch", "searchnext"])
    async def search(self, ctx):
        """Searches and plays a song from youtube"""
        # get song query
        query = self.get_query(ctx)

        # send standard searching message
        message = await self.searching_message(ctx, query)

        # get videos from youtube
        video_results = VideosSearch(query, limit=4).result()['result']

        # send search results with selection menu
        lookup_message = f"Search results for `{query}`:\n"
        for i, result in enumerate(video_results):
            lookup_message += f"{from_numbers(i + 1)} `{result['title']}` - `[{result['duration']}]`\n"
        await message.edit(content=lookup_message)

        # respond to selection menu
        reaction, sender = await BotUtils.numbered_reaction_menu(self.bot, message, len(video_results), ctx.author)
        if reaction is not None:
            song_data = video_results[reaction-1]
            song = dict_to_song(song_data, ctx.author)

            # add song to queue and send standard added to queue message
            await self.add_to_queue_message(message, song.name)
            self.add_to_queue(ctx.guild.id, song, ctx.invoked_with in ["nextsearch", "searchnext"])

    @commands.command(aliases=["nextplay", "playnext"])
    async def play(self, ctx):
        """Plays a song from youtube"""
        query = self.get_query(ctx)

        message = await self.searching_message(ctx, query)

        # handles for when a youtube playlist is passed in
        if query.startswith("https://www.youtube.com/playlist?list="):
            playlist = Playlist.getVideos(query)
            videos = playlist["videos"]
            add_to_start = ctx.invoked_with in ["nextplay", "playnext"]

            # insures that videos are put in the correct order when inserted to the front of the queue
            if add_to_start:
                videos.reverse()

            for video in videos:
                song = dict_to_song(video, ctx.author)
                self.add_to_queue(ctx.guild.id, song, add_to_start)

            await message.edit(content=f":white_check_mark: Added a playlist with {len(videos)} songs to the queue")

            return

        video_result = VideosSearch(query, limit=1).result()['result'][0]
        song = dict_to_song(video_result, ctx.author)

        # add song to queue and send standard added to queue message
        await self.add_to_queue_message(message, song.name)
        self.add_to_queue(ctx.guild.id, song, ctx.invoked_with in ["nextplay", "playnext"])

    @commands.command()
    async def queue(self, ctx):
        """Displays the server's song queue"""
        queue = queues[ctx.guild.id]
        message_text = "Song queue:\n"
        for i, song in enumerate(queue.songs):
            message_text += f"{i+1}. `{song.duration}` {song.name}\n"
        await ctx.send(message_text)

    @commands.command()
    async def clearqueue(self, ctx):
        """Clears a guild's queue"""
        queues.remove_queue(ctx.guild.id)
        await ctx.send(":white_check_mark: Cleared the queue")

    @commands.command()
    async def stop(self, ctx):
        """disconnects from current voice channel"""
        await ctx.voice_client.disconnect()
        queues.remove_queue(ctx.guild.id)


def setup(bot):
    bot.add_cog(Music(bot))
