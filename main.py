"""
Main entry point for the Kasutamaiza Bot.
- Initializes the bot, performs permissions checks, and loads command modules (cogs).
"""

import os
import time
import discord
from discord.ext import commands
from dotenv import load_dotenv
from loguru import logger

# Metadata
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
BOT_TYPE = "Slash Command-Based"

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))  # Replace with your actual server ID in the .env file

# Set up logging
logger.add("bot.log", rotation="10 MB", retention="10 days", backtrace=True, diagnose=True)

# Intents for the bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot setup
bot = discord.Bot(intents=intents, guilds=[discord.Object(id=GUILD_ID)])  # Restrict to a specific guild


@bot.event
async def on_ready():
    """
    Triggered when the bot is successfully logged in.
    """
    logger.info(f"Bot is online as {bot.user}")
    logger.info(f"Bot Type: {BOT_TYPE}")
    logger.info(f"Connected to Guild: {GUILD_ID}")

    # Perform permissions check
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            await check_permissions(guild)
        else:
            logger.warning(f"Bot could not retrieve the guild with ID: {GUILD_ID}")
    except Exception as e:
        logger.error(f"Failed to check permissions: {e}")

    # Load cogs with time measurement
    try:
        logger.info("Loading cogs...")
        await load_cogs(bot)
        logger.info("Cogs loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load cogs: {e}")
        logger.exception(e)

    # Sync commands and measure time
    try:
        logger.info("Starting command sync with Discord...")
        start_time = time.monotonic()
        await bot.sync_commands()
        elapsed_time = time.monotonic() - start_time
        logger.info(f"Slash commands synced successfully in {elapsed_time:.2f} seconds.")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

    # Log all registered slash commands
    try:
        log_registered_commands()
    except Exception as e:
        logger.error(f"Failed to log registered commands: {e}")


async def check_permissions(guild: discord.Guild):
    """
    Check if the bot has the required permissions in the guild.
    """
    required_permissions = [
        "administrator",
        "manage_guild",
        "manage_roles",
        "send_messages",
        "manage_messages",
        "read_message_history",
        "manage_channels",
    ]

    bot_member = guild.me
    missing_perms = [
        perm for perm in required_permissions
        if not getattr(bot_member.guild_permissions, perm, False)
    ]

    if missing_perms:
        logger.warning(f"Bot is missing the following permissions in guild {guild.name} ({guild.id}): {missing_perms}")
    else:
        logger.info(f"Bot has all required permissions in guild {guild.name} ({guild.id}).")


async def load_cogs(bot: discord.Bot):
    """
    Dynamically loads all command modules (cogs) from the 'cogs' directory.
    """
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            module_name = f'cogs.{filename[:-3]}'
            try:
                logger.debug(f"Attempting to load cog: {module_name}")
                module = __import__(module_name, fromlist=['setup'])

                # Ensure `setup` function is present and callable
                if hasattr(module, 'setup') and callable(module.setup):
                    start_time = time.monotonic()
                    module.setup(bot, GUILD_ID)  # Pass the `GUILD_ID` to the cog setup
                    elapsed_time = time.monotonic() - start_time
                    logger.info(f"Successfully loaded cog: {module_name} in {elapsed_time:.2f} seconds.")
                else:
                    logger.error(f"Cog {module_name} is missing a valid 'setup' function.")
            except Exception as e:
                logger.error(f"Failed to load cog {module_name}: {e}")
                logger.exception(e)


def log_registered_commands():
    """
    Log all registered slash commands and their options.
    """
    logger.info("Registered Slash Commands:")
    for cmd in bot.application_commands:
        logger.info(
            f" - Command: {cmd.name} | Description: {cmd.description} | Guild ID(s): {cmd.guild_ids or 'Global'}"
        )
        
        # Log options if available
        if hasattr(cmd, 'options') and cmd.options:
            option_details = ", ".join(
                [f"{opt.name} ({opt.input_type})" for opt in cmd.options if hasattr(opt, 'input_type')]
            )
            logger.info(f"   Options: {option_details}")
        else:
            logger.info("   Options: None")

    if not bot.application_commands:
        logger.warning("No slash commands are registered.")


if __name__ == "__main__":
    try:
        logger.info("Starting Kasutamaiza Bot...")
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")
        logger.exception(e)