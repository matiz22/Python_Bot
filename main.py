import os
import discord
from discord.ext import commands
from discord.ext.commands import bot
from dotenv import load_dotenv


class abot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())
        self.synced = False
        self.initial_extensions = []

    # Metoda do ładowania Cogow z folderu Cogs
    async def setup_hook(self):
        for fname in os.listdir('./Cogs'):
            if fname.endswith('.py'):
                await self.load_extension(f'Cogs.{fname[:-3]}')
        await bot.tree.sync()
        print(f"we have logged in as {self.user}")

    async def on_ready(self):
        #tempunban.start()
        await self.wait_until_ready()
        if not self.synced:
            await bot.tree.sync()  # jesli jest puste bot updatuje komendy na wszystkich serwerach, mozna podac id serwera/ liste id
            self.synced = True

        print(f"we have logged in as {self.user}")


load_dotenv()
bot = abot()
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)


