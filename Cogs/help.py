import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name="help", description="pomoc")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Pomoc",
                              description="Instrukcja korzystania z bota",
                              color=discord.Color.yellow(),
                              )
        embed.set_thumbnail(
            url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQPB17cZaaULuOWi2QGCg-l1tQX9b9oGjvILPGSnu4nPg&s")
        embed.add_field(name="**/help**", value="Pokazuje poradnik korzystania z bota", inline=False)
        embed.add_field(name="**/google**", value="Wysyła przycisk z linkiem wyszukiwania w googlu", inline=False)
        embed.add_field(name="**/mem**", value="Wysyła losowego mema", inline=False)
        embed.add_field(name="**/log**", value="Tworzy z kanał do logów", inline=False)
        embed.add_field(name="**/rps**", value="Gra w papier, kamień, nożyce", inline=False)
        embed.add_field(name="**/tempban**", value="Tymczasowa blokada na serwer", inline=False)
        embed.add_field(name="**/unban**", value="Odbanowanie", inline=False)
        embed.add_field(name="**/lista_zbanowanych**", value="Lista zbanowanych użytkowników", inline=False)
        embed.add_field(name="**/reactionroles**", value="Tworzy wiadomość na wybranym kanale do dodawania ról",
                        inline=False)
        embed.add_field(name="**/play**",
                        value="Bot wchodzi na kanal, na ktorym znajduje sie uzytkownik, i puszcza podana piosenke z yt",
                        inline=False)
        embed.add_field(name="**/pause**",
                        value="Bot pauzuje muzyke",
                        inline=False)
        embed.add_field(name="**/resume**",
                        value="Bot wznawia muzyke",
                        inline=False)
        embed.add_field(name="**/dolacz**",
                        value="Bot wchodzi tylko na kanal",
                        inline=False)
        embed.add_field(name="**/wyjdz**",
                        value="Bot wychodzi z kanalu",
                        inline=False)
        embed.add_field(name="**/czysc**",
                        value="czysci kolejke",
                        inline=False)
        embed.add_field(name="**/skip**",
                        value="przechodzi do nastepnej piosenki",
                        inline=False)
        embed.add_field(name="**/kolejka**",
                        value="Pokazuje liste piosenek ktore zostana puszczone",
                        inline=False)


        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot))
