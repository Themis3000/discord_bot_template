import asyncio
import youtube_dl
from youtubesearchpython import VideosSearch, Playlist, Video
from discord.ext import commands
import discord
from collections import deque

from utils.emoji import from_numbers
from utils.bot import BotUtils
from utils.time import convert_millis_str


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Song:
    """A single song"""
    def __init__(self, url, name, duration, adder=None):
        self.url = url
        self.name = name
        self.duration = duration
        self.adder = adder
        self.data = None


class Queue:
    """A single queue"""
    def __init__(self, bot):
        self.songs = deque()
        self.bot = bot

    async def play_song(self, song: Song, voice_client, after=None):
        player = await self.create_player(song)
        if after is not None:
            voice_client.play(player, after=after)
            return
        voice_client.play(player)

    async def create_player(self, song: Song):
        return await YTDLSource.from_url(song.url, stream=True, loop=self.bot.loop)

    async def execute_queue(self, voice_client):

        def after(e=None):
            if e is not None:
                print(f"An error occurred while playing: {e}")
            coro = self.execute_queue(voice_client)
            fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"The following error occurred while trying to call the after function: {e}")

        if self.__len__() > 0 and voice_client is not None:
            song = self.pop_left()
            await self.play_song(song, voice_client, after)

    def pop_left(self) -> Song:
        """Removes the next up song from the queue and also returns it"""
        return self.songs.popleft()

    async def play_if_stopped(self, voice_client):
        if voice_client is None:
            return
        if not voice_client.is_playing():
            await self.execute_queue(voice_client)

    def add_song(self, song: Song, start=False):
        """Adds a song to the queue"""
        if start:
            self.songs.appendleft(song)
            return
        self.songs.append(song)

    def __len__(self) -> int:
        """Gets the item length of the queue (as opposed to time length)"""
        return len(self.songs)


class Queues:
    def __init__(self, bot):
        self.guilds = {}
        self.bot = bot

    def __getitem__(self, guild: discord.Guild) -> Queue:
        """Gets the queue for a given guild. If none exists, one if created"""
        if guild.id not in self.guilds:
            self.guilds[guild.id] = Queue(self.bot)
        return self.guilds[guild.id]

    def remove_queue(self, guild: discord.Guild):
        """Removes a given guild's queue"""
        try:
            self.guilds.pop(guild.id)
        except KeyError:
            pass

    def __delitem__(self, guild: discord.Guild):
        """Removes a given guild's queue"""
        self.remove_queue(guild)


def dict_to_song(search_dict: dict, author: discord.User) -> Song:
    """Converts the dictionary provided by youtubesearchpython to a Song object"""
    return Song(search_dict['link'],
                search_dict['title'],
                search_dict['duration'],
                author)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = Queues(bot)

    @commands.command()
    async def join(self, ctx: discord.ext.commands.Context):
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

    async def queue_and_unpause(self, guild: discord.Guild, song, add_to_start):
        """Adds a song to a given guild's queue"""
        queue = self.queues[guild]
        queue.add_song(song, add_to_start)
        await queue.play_if_stopped(guild.voice_client)

    @staticmethod
    def get_query(ctx: discord.ext.commands.Context) -> str:
        return ctx.message.content[len(ctx.invoked_with) + 2:]

    @commands.command(aliases=["nextsearch", "searchnext"])
    async def search(self, ctx: discord.ext.commands.Context):
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
            await self.queue_and_unpause(ctx.guild, song, ctx.invoked_with in ["nextsearch", "searchnext"])

    @commands.command(aliases=["nextplay", "playnext"])
    async def play(self, ctx: discord.ext.commands.Context):
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
                await self.queue_and_unpause(ctx.guild, song, add_to_start)

            await message.edit(content=f":white_check_mark: Added a playlist with {len(videos)} songs to the queue")
            return

        if query.startswith("https://www.youtube.com/watch?v="):
            video_result = Video.get(query)
            print(video_result)
            video_result["duration"] = convert_millis_str(int(video_result["streamingData"]["formats"][0]["approxDurationMs"]))
        else:
            video_result = VideosSearch(query, limit=1).result()["result"][0]

        song = dict_to_song(video_result, ctx.author)

        # add song to queue and send standard added to queue message
        await self.add_to_queue_message(message, song.name)
        await self.queue_and_unpause(ctx.guild, song, ctx.invoked_with in ["nextplay", "playnext"])

    @commands.command(aliases=["unplay", "deplay"])
    async def pause(self, ctx: discord.ext.commands.Context):
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            await ctx.send(":pause_button: **Paused**")

    @commands.command(aliases=["unpause", "depause"])
    async def resume(self, ctx: discord.ext.commands.Context):
        voice_client = ctx.voice_client
        if voice_client.is_paused():
            voice_client.resume()
            await ctx.send(":play_pause: **Resuming**")

    @commands.command()
    async def queue(self, ctx: discord.ext.commands.Context):
        """Displays the server's song queue"""
        queue = self.queues[ctx.guild]

        if len(queue) == 0:
            await ctx.send(":x: The queue is currently empty")
            return

        message_text = "Song queue:\n"
        for i, song in enumerate(queue.songs):
            message_text += f"{i+1}. `{song.duration}` {song.name}\n"
        await ctx.send(message_text)

    @commands.command(aliases=["queueclear"])
    async def clearqueue(self, ctx: discord.ext.commands.Context):
        """Clears a guild's queue"""
        self.queues.remove_queue(ctx.guild)
        await ctx.send(":white_check_mark: Cleared the queue")

    @commands.command(aliases=["leave"])
    async def stop(self, ctx: discord.ext.commands.Context):
        """disconnects from current voice channel"""
        await ctx.voice_client.disconnect()
        self.queues.remove_queue(ctx.guild)


def setup(bot):
    bot.add_cog(Music(bot))
