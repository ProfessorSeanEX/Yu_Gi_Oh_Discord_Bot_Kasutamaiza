"""
Main entry point for the Kasutamaiza Bot.
- Initializes the bot and loads command modules (cogs).
- Maintains scalability and separation of concerns.
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from loguru import logger

# Metadata
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "A Discord bot to enhance Yu-Gi-Oh experiences and server engagement."

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Set up logging
logger.add("bot.log", rotation="10 MB", retention="10 days")

# Intents for the bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required for member-related commands

# Bot setup
bot = commands.Bot(command_prefix=">>", intents=intents)

@bot.event
async def on_ready():
    """
    Triggered when the bot is successfully logged in.
    """
    bot.remove_command("help")  # Remove default help command
    logger.info(f"Bot is online as {bot.user}")
    await load_cogs(bot)  # Properly await the async function
    print("Registered commands after cog loading:")
    for command in bot.commands:
        print(f"Prefix Command: {command.name}")
    for slash_command in bot.application_commands:
        print(f"Slash Command: {slash_command.name}")

async def load_cogs(bot):
    """
    Dynamically loads all command modules (cogs) from the 'cogs' directory.
    """
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                # Import module and await its setup function
                module_name = f'cogs.{filename[:-3]}'
                module = __import__(module_name, fromlist=['setup'])
                await module.setup(bot)  # Await the setup function
                logger.info(f"Loaded cog: {filename[:-3]}")
                print(f"Loaded cog: {filename[:-3]}")
            except Exception as e:
                logger.error(f"Failed to load cog {filename[:-3]}: {e}")
                logger.exception(e)

if __name__ == "__main__":
    bot.run(TOKEN)