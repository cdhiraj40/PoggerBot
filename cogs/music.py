import discord
import youtube_dl
from discord.ext import commands
from discord.utils import get
import asyncio
import functools

cur_queue = []
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()
        partial = functools.partial(ytdl.extract_info, f"ytsearch1:{url}", download=False)

        data = await loop.run_in_executor(None, partial)

        if data is None:
            return print('Couldn\'t find anything that matches `{}`'.format(url))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break
            if process_info is None:
                return print('Couldn\'t find anything that matches `{}`'.format(url))

        processed_info = await loop.run_in_executor(None, partial)
        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    return print('Couldn\'t retrieve any matches for `{}`'.format(url))
        video_title = info['title']
        return (discord.FFmpegPCMAudio(info["url"], **ffmpeg_options)), video_title


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client  # this allows us to access the client within our cog

    def check_queue(self, ctx):
        if len(cur_queue) != 0:
            song_url = cur_queue[0][1]
            cur_queue.remove(cur_queue[0])
            voice_channel = get(self.client.voice_clients, guild=ctx.guild)
            voice_channel.play(song_url, after=lambda e: self.check_queue(ctx))
            return

    @commands.command(aliases=["j"], help='Tells the bot to join the voice channel')
    async def join(self, ctx):
        try:
            if not ctx.message.author.voice:
                await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
                return
            else:
                channel = ctx.message.author.voice.channel
            await channel.connect()
        except Exception as e:
            print(e)
            await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))

    @commands.command(aliases=["l"], help='To make the bot leave the voice channel')
    async def leave(self, ctx):
        try:
            voice_client = ctx.message.guild.voice_client
            if voice_client.is_connected():
                await voice_client.disconnect()
            else:
                await ctx.send("The bot is not connected to a voice channel.")
        except Exception as e:
            print(e)
            await ctx.send("The bot is not connected to a voice channel.")

    @commands.command(aliases=["pa"], help='This command pauses the song')
    async def pause(self, ctx):
        try:
            voice_client = ctx.message.guild.voice_client
            if voice_client.is_playing():
                voice_client.pause()
                await ctx.send("Music has been paused!")
            else:
                await ctx.send("Nothing is currently playing! Use the play command!")
        except Exception as e:
            print(e)
            await ctx.send("Nothing is currently playing! Use the play command!")

    @commands.command(aliases=["re"], help='Resumes the song')
    async def resume(self, ctx):
        try:
            voice_client = ctx.message.guild.voice_client
            if voice_client.is_paused():
                voice_client.resume()
                await ctx.send("Music has resumed!")
            else:
                await ctx.send("Nothing is currently playing! Use the play command!")
        except Exception as e:
            print(e)
            await ctx.send("Nothing is currently playing! Use the play command!")

    @commands.command(aliases=["st"], help='Stops the song')
    async def stop(self, ctx):
        try:
            voice_client = ctx.message.guild.voice_client
            if len(cur_queue) != 0:
                cur_queue.clear()
            elif voice_client.is_playing():
                voice_client.stop()
                await ctx.send("Stopping the music! The queue is now clear!")
            else:
                await ctx.send("Nothing is currently playing! Use the play command!")
        except Exception as e:
            print(e)
            await ctx.send("Nothing is currently playing! Use the play command!")

    @commands.command(aliases=["add_queue", "a", "p", "pl", "play"])
    async def add(self, ctx, *, urls):
        song_list = []
        if '&' in str(urls):
            song_list = urls.split(' & ')
        else:
            song_list.append(urls)

        for url in song_list:
            try:
                async with ctx.typing():
                    song, video_title = await YTDLSource.from_url(url, loop=self.client.loop)
                    voice = get(self.client.voice_clients, guild=ctx.guild)
                    if len(cur_queue) == 0:
                        if not voice:
                            if not ctx.message.author.voice:
                                return await ctx.send(
                                    "{} is not connected to a voice channel".format(ctx.message.author.name))
                            channel = ctx.message.author.voice.channel
                            await channel.connect()
                            voice_channel = get(self.client.voice_clients, guild=ctx.guild)
                            voice_channel.play(song, after=lambda e: self.check_queue(ctx))
                            await ctx.send('**Now playing:** {}'.format(video_title))
                            continue
                        elif voice and not bool(voice.is_playing()):
                            voice_channel = get(self.client.voice_clients, guild=ctx.guild)
                            voice_channel.play(song, after=lambda e: self.check_queue(ctx))
                            await ctx.send('**Now playing:** {}'.format(video_title))
                            continue
                    cur_queue.append([video_title, song])

                await ctx.send('**Song added to queue:** {}'.format(video_title))
            except Exception as e:
                print(e)
                return await ctx.send("Unable to add songs to queue, please try again... "
                                      "\n\nWas I already adding songs?")

    @commands.command(aliases=["r, removequeue"])
    async def remove(self, ctx, *, song_position):
        msg = f"**Removed:** {cur_queue[int(song_position) - 1][0]}"
        del cur_queue[int(song_position) - 1]
        await ctx.send(msg)

    @commands.command(aliases=["show_queue", "q"])
    async def queue(self, ctx):
        msg_queue = [f"**{i}** - {song[0]}" for i, song in enumerate(cur_queue, start=1)]
        await ctx.send("**Current Queue:** \n" + "\n".join(msg_queue))

    @commands.command(aliases=["n", "skip", "s", "sk"])
    async def next(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.stop()
            try:
                song_name = cur_queue[0][0]
                if song_name:
                    if len(cur_queue) > 1:
                        return await ctx.channel.send(
                            f'**Skipping... Now playing:** {song_name}' + f'\n**Up Next!:** {cur_queue[1][0]}')
                    else:
                        return await ctx.channel.send(
                            f'**Skipping... Now playing:** {song_name}' + '\n**The queue is now empty!**')
            except Exception as e:
                print(e)
                print("No Music playing - failed to play next song")
                return await ctx.send("No music currently playing...")

        print("No Music playing - failed to play next song")
        await ctx.send("No music currently playing...")


# This function allows us to connect this cog to our bot
def setup(client):
    client.add_cog(Music(client))
