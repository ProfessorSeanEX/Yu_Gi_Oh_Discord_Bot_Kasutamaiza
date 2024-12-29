"""
Main entry point for the Kasutamaiza Bot.
- Initializes the bot and loads command modules (cogs).
- Maintains scalability and separation of concerns.
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Metadata: Bot info
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "A Discord bot to enhance Yu-Gi-Oh experiences and server engagement."

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Intents for the bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required for member-related commands

# Bot setup
bot = commands.Bot(command_prefix=">>", intents=intents)

# Metadata: Commands list
__commands__ = ["ping", "info", "help", "kick", "ban"]

@bot.event
async def on_ready():
    """Triggered when the bot is successfully logged in."""
    print(f"Bot is online as {bot.user}")
    await load_cogs(bot)

async def load_cogs(bot):
    """
    Dynamically loads all command modules (cogs) from the 'cogs' directory.
    """
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Loaded cog: {filename[:-3]}')

# Run the bot
if __name__ == "__main__":
    bot.run(TOKEN)