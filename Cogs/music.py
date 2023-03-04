import discord
from discord import app_commands
from discord.ext import commands
from asyncio import run_coroutine_threadsafe
from urllib import parse, request
import re
from yt_dlp import YoutubeDL


class music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.czyGra = {}
        self.czyPauza = {}
        self.kolejkaMuzyki = {}
        self.kolejkaIndexow = {}
        self.vc = {}
        self.YTDL_OPTIONS = {
            'format': 'bestaudio',
            'nonplaylist': 'True',
            'youtube_include_dash_manifest': False,
        }

        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            id = int(guild.id)
            self.kolejkaMuzyki[id] = []
            self.kolejkaIndexow[id] = 0
            self.vc[id] = None
            self.czyPauza[id] = self.czyGra[id] = False

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        id = int(guild.id)
        self.kolejkaMuzyki[id] = []
        self.kolejkaIndexow[id] = 0
        self.vc[id] = None
        self.czyPauza[id] = self.czyGra[id] = False

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        id = int(member.guild.id)
        if member.id != self.bot.user.id and before.channel != None and after.channel != before.channel:
            remainingChannelMembers = before.channel.members
            if len(remainingChannelMembers) == 1 and remainingChannelMembers[0].id == self.bot.user.id and self.vc[
                id].is_connected():
                self.czyGra[id] = self.czyPauza[id] = False
                self.kolejkaMuzyki[id] = []
                self.kolejkaIndexow[id] = 0
                await self.vc[id].disconnect()

    async def join_vc(self, interaction: discord.Interaction, channel):
        id = int(interaction.guild.id)
        if self.vc[id] == None or not self.vc[id].is_connected():
            self.vc[id] = await channel.channel.connect()
            if self.vc[id] == None:
                await interaction.response.send_message("blad polaczenia")
                return
        else:
            await self.vc[id].move_to(channel.channel)

    def search_YT(self, search):
        queryString = parse.urlencode({'search_query': search})
        htmContent = request.urlopen('http://www.youtube.com/results?' + queryString)
        searchResults = re.findall(
            '/watch\?v=(.{11})', htmContent.read().decode())
        return searchResults[0:10]

    def extract_YT(self, url):
        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except:
                return False
            source = ""
            for y in info["formats"]:
                if y["audio_ext"] == 'webm':
                    source = y['url']
                    break
            print(source, "cos")
        return {
            'link': 'https://www.youtube.com/watch?v=' + url,
            'thumbnail': 'https://i.ytimg.com/vi/' + url + '/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig',
            'source': source,
            'title': info['title']
        }

    def play_next(self, interaction: discord.Interaction):
        id = int(interaction.guild.id)
        if not self.czyGra[id]:
            return
        if self.kolejkaIndexow[id] + 1 < len(self.kolejkaMuzyki[id]):
            self.czyGra[id] = True
            self.kolejkaIndexow[id] += 1

            song = self.kolejkaMuzyki[id][self.kolejkaIndexow[id]][0]
            message = self.now_playing_embed(interaction, song)
            coro = interaction.response.send_message(embed=message)
            fut = run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except:
                pass

            self.vc[id].play(discord.FFmpegPCMAudio(
                song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(interaction))
        else:
            self.kolejkaIndexow[id] += 1
            self.czyGra[id] = False

    async def play_music(self, interaction: discord.Interaction):
        id = int(interaction.guild.id)
        if self.kolejkaIndexow[id] < len(self.kolejkaMuzyki[id]):
            self.czyPauza[id] = True
            self.czyGra[id] = False

            await self.join_vc(interaction, self.kolejkaMuzyki[id][self.kolejkaIndexow[id]][1])
            song = self.kolejkaMuzyki[id][self.kolejkaIndexow[id]][0]
            message = self.now_playing_embed(interaction, song)
            await interaction.response.send_message(embed=message)
            self.vc[id].play(discord.FFmpegPCMAudio(
                song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(interaction))
        else:
            await interaction.response.send_message("Nie ma pioseneke w kolejce")
            self.kolejkaIndexow[id] += 1
            self.czyGra[id] = False

    def now_playing_embed(self, interaction: discord.Interaction, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = interaction.user
        avatar = author.avatar.url
        embed = discord.Embed(
            title=title,
            description=f"[{title}({link})]",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f"Piosenke puścił: {author}", icon_url=avatar)
        return embed

    def queue_embed(self, interaction: discord.Interaction, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = interaction.user
        avatar = author.avatar.url
        embed = discord.Embed(
            title="Zakolejkowano",
            color=discord.Color.red()
        )
        embed.add_field(name="nutke", value=title)
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f"Piosenke puścił: {author}", icon_url=avatar)
        return embed

    @app_commands.command(name="play", description="puszcza muzyke z yt przez podany link")
    async def play(self, interaction: discord.Interaction, link_szukaj: str):
        id = interaction.guild.id
        try:
            userChannel = interaction.user.voice
        except:
            await interaction.response.send_message("wez sie podlacz")
            return
        if link_szukaj is None or link_szukaj == "":
            if len(self.kolejkaMuzyki[id] == 0):
                await interaction.response.send_message("Nie ma piosenek w kolejce")
                return
            elif not self.czyGra[id]:
                if self.kolejkaMuzyki[id] == None or self.vc[id] == None:
                    await self.play_music(interaction)
                else:
                    self.czyPauza[id] = False
                    self.czyGra[id] = True
                    self.vc[id].resume()
            else:
                return
        else:
            song = self.extract_YT(self.search_YT(link_szukaj)[0])
            if type(song) == type(True):
                await interaction.response.send_message("Nie znaleziono")
            else:
                self.kolejkaMuzyki[id].append([song, userChannel])
                if not self.czyGra[id]:
                    await self.play_music(interaction)
                    self.czyPauza[id] = False
                    self.czyGra[id] = True
                else:
                    await interaction.response.send_message(embed=self.queue_embed(interaction=interaction, song=song))

    @app_commands.command(name="dolacz", description="dolacza na kanał")
    async def dolacz(self, interaction: discord.Interaction):
        voice_state = interaction.user.voice
        if not voice_state is None:
            # userChannel = interaction.message.author.voice.channel
            await self.join_vc(interaction, interaction.user.voice)
            await interaction.response.send_message("Połączono")
        else:
            await interaction.response.send_message("Musisz być na kanale")

    @app_commands.command(name="wyjdz", description="wychodzi z kanału")
    async def wyjdz(self, interaction: discord.Interaction):
        id = int(interaction.guild.id)
        self.czyGra[id] = self.czyPauza[id] = False
        self.kolejkaMuzyki[id] = []
        self.kolejkaIndexow[id] = 0
        if not self.vc[id] is None:
            await interaction.response.send_message("Bot wyszedł z kanału")
            await self.vc[id].disconnect()

    @app_commands.command(name="pause", description="Pauzuje muzyke")
    async def pause(self, interaction: discord.Interaction):
        id = int(interaction.guild.id)
        if not self.vc[id]:
            await interaction.response.send_message("Nie ma czego pauzować")
        elif self.czyGra[id]:
            await interaction.response.send_message("Pauze")
            self.czyGra[id] = False
            self.czyPauza[id] = True
            self.vc[id].pause()

    @app_commands.command(name="resume", description="Wznawia muzyke")
    async def resume(self, interaction: discord.Interaction):
        id = int(interaction.guild.id)
        if not self.vc[id]:
            await interaction.response.send_message("Nie ma czego wznawiac")
        elif not self.czyGra[id]:
            self.czyGra[id] = False
            self.czyPauza[id] = True
            self.vc[id].resume()
            await interaction.response.send_message("leci")

    @app_commands.command(name="cofnij", description="cofa kolejke")
    async def cofnij(self, interaction: discord.Interaction):
        id = int(interaction.guild.id)
        if self.vc[id] == None:
            await interaction.response.send_message("Wejdz na kanal")
        elif len(self.kolejkaMuzyki[id]) <= 0:
            await interaction.response.send_message("Powtarzam")
            self.vc[id].pause()
            await self.play_music(interaction)
        elif self.vc[id] != None and self.vc[id]:
            self.vc[id].pause()
            self.kolejkaIndexow[id] -= 1
            await self.play_music(interaction)

    @app_commands.command(name="skip", description="pomija nutke")
    async def skip(self, interaction: discord.Interaction):
        id = int(interaction.guild.id)
        if self.vc[id] == None:
            await interaction.response.send_message("Wejdz na kanal")
        elif self.kolejkaIndexow[id] >= len(self.kolejkaMuzyki[id]) - 1:
            await interaction.response.send_message("Powtarzam")
            self.vc[id].pause()
            await self.play_music(interaction)
        elif self.vc[id] != None and self.vc[id]:
            self.vc[id].pause()
            self.kolejkaIndexow[id] += 1
            await self.play_music(interaction)

    @app_commands.command(name="kolejka", description="nutki w kolejce")
    async def kolejka(self, interaction: discord.Interaction):
        id = int(interaction.guild.id)
        returnValue = ""
        if self.kolejkaMuzyki[id] == []:
            await interaction.response.send_message("Nie ma nutek w kolejce")
            return

        for i in range(self.kolejkaIndexow[id], len(self.kolejkaMuzyki[id])):
            upNextSongs = len(self.kolejkaMuzyki[id]) - self.kolejkaIndexow[id]
            if i > 5 + upNextSongs:
                break
            returnIndex = i - self.kolejkaIndexow[id]
            if returnIndex == 0:
                returnIndex = "Teraz"
            elif returnIndex == 1:
                returnIndex = "Nastepna"
            returnValue += f"{returnIndex} - [{self.kolejkaMuzyki[id][i][0]['title']}]({self.kolejkaMuzyki[id][i][0]['link']})\n"

            if returnValue == "":
                await interaction.response.send_message("Nie ma nutek w kolejce")
                return

        queue = discord.Embed(
            title="Kolejka",
            description=returnValue,
            colour=discord.Color.red()
        )
        await interaction.response.send_message(embed=queue)

    @app_commands.command(name="czysc", description="czysci kolejke")
    async def clear(self, interaction: discord.Interaction):
        id = int(interaction.guild.id)
        if self.vc[id] != None and self.czyGra[id]:
            self.czyGra[id] = self.czyPauza[id] = False
            self.vc[id].stop()
        if self.kolejkaMuzyki[id] != []:
            await interaction.response.send_message("Puściutko")
            self.kolejkaMuzyki[id] = []
        self.queueIndex = 0


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(music(bot))