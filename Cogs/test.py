from discord import app_commands
from discord.ext import commands
import discord
import random

#Gotowy Cog do skopiowania
class Nazwa(commands.Cog):
    def __init__ (self, bot) -> None:
        self.bot = bot



async def setup (bot: commands.Bot) -> None:
    await bot.add_cog(Nazwa(bot))

