import json
from urllib.parse import quote_plus
import discord
import requests
from discord import app_commands
from discord.ext import commands


class Inne(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name="mem", description="losowy mem")
    async def memik(self, interaction: discord.Interaction):
        czyNSFW = True
        await interaction.response.send_message("Szukam")
        while czyNSFW:
            content = requests.get("https://meme-api.com/gimme/1").content
            data = json.loads(content)
            if czyNSFW != data['memes'][0]['nsfw']:
                meme = discord.Embed(title=f"{data['memes'][0]['title']}", color=discord.Color.random()).set_image(
                    url=f"{data['memes'][0]['url']}")
                await interaction.channel.send(embed=meme)
                break

    # Wyszukanie linku
    @app_commands.command(name="google", description="podaj link wyszukiwania")
    async def google(self, interaction: discord.Interaction, query: str):
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Twoje wyszukiwanie", url=url))
        await interaction.response.send_message(view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Inne(bot))
