"""
Main entry point for the Kasutamaiza Bot.
- Initializes the bot, performs permissions checks, loads command modules (cogs), and utility modules (utils).
"""

import os
import time
import asyncio  # For concurrent tasks
import discord
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv  # Enhanced loading for dotenv
from loguru import logger
from datetime import datetime, timedelta, timezone  # Import timezone for UTC

import sys
sys.path.append('/opt/kasutamaiza-bot')  # Add the directory explicitly
from db_manager import db_manager


# Metadata
__version__ = "1.3.0"
__author__ = "ProfessorSeanEX"
BOT_TYPE = "Slash Command-Based"

# Load environment variables
if not load_dotenv(find_dotenv()):  # Attempt to load .env file
    logger.critical("Failed to load .env file. Ensure the file exists and is correctly configured.")
    exit(1)

# Load environment variables
TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

if not TOKEN or not GUILD_ID:
    logger.critical("Environment variables BOT_TOKEN or GUILD_ID are missing or invalid. Exiting.")
    exit(1)

GUILD_ID = int(GUILD_ID)

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

    # Initialize database connection pool
    try:
        await db_manager.initialize_pool()
        logger.info("Database connection pool initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database pool: {e}")
        exit(1)

    # Perform permissions check
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            await check_permissions(guild)
        else:
            logger.warning(f"Bot could not retrieve the guild with ID: {GUILD_ID}")
    except Exception as e:
        logger.error(f"Failed to check permissions: {e}")

    # Load cogs and utils concurrently
    try:
        logger.info("Starting cog and utility module loading...")
        await asyncio.gather(load_cogs(bot), load_utils(), bot.sync_commands())
        logger.info("Cogs and utilities loaded successfully. Commands synced.")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

    # Log all registered slash commands
    try:
        log_registered_commands()
    except Exception as e:
        logger.error(f"Failed to log registered commands: {e}")

    # Set bot uptime
    bot.start_time = datetime.now(timezone.utc)  # Set start time when the bot becomes ready

    # Start heartbeat task
    bot.loop.create_task(heartbeat())


async def heartbeat():
    """
    Logs a heartbeat message periodically to indicate the bot is running.
    """
    while True:
        try:
            logger.info("Heartbeat: Bot is online and operational.")
            # Use timezone-aware datetime for UTC
            await discord.utils.sleep_until(datetime.now(timezone.utc) + timedelta(minutes=10))
        except Exception as e:
            logger.error(f"Heartbeat encountered an error: {e}")


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
    if not os.path.exists('./cogs'):
        logger.critical("Cogs directory './cogs' does not exist. Exiting.")
        exit(1)

    failed_cogs = 0
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            module_name = f'cogs.{filename[:-3]}'
            try:
                logger.debug(f"Attempting to load cog: {module_name}")
                module = __import__(module_name, fromlist=['setup'])

                # Ensure `setup` function is present and callable
                if hasattr(module, 'setup') and callable(module.setup):
                    start_time = time.monotonic()
                    module.setup(bot, GUILD_ID, TOKEN)  # Pass GUILD_ID and TOKEN
                    elapsed_time = time.monotonic() - start_time
                    logger.info(f"Successfully loaded cog: {module_name} in {elapsed_time:.2f} seconds.")
                else:
                    logger.error(f"Cog {module_name} is missing a valid 'setup' function.")
            except Exception as e:
                failed_cogs += 1
                logger.error(f"Failed to load cog {module_name}: {e}")

    if failed_cogs > 0:
        logger.warning(f"{failed_cogs} cog(s) failed to load.")


async def load_utils():
    """
    Dynamically loads all utility modules from the 'utils' directory.
    """
    if not os.path.exists('./utils'):
        logger.warning("Utilities directory './utils' does not exist. Skipping utility loading.")
        return

    failed_utils = 0
    for filename in os.listdir('./utils'):
        if filename.endswith('.py'):
            module_name = f'utils.{filename[:-3]}'
            try:
                logger.debug(f"Attempting to load utility module: {module_name}")
                module = __import__(module_name)
                if hasattr(module, 'initialize') and callable(module.initialize):
                    await module.initialize()  # Call initialize function if present
                    logger.info(f"Successfully initialized utility module: {module_name}")
                else:
                    logger.warning(f"Utility module {module_name} has no 'initialize' function.")
            except Exception as e:
                failed_utils += 1
                logger.error(f"Failed to load utility module {module_name}: {e}")

    if failed_utils > 0:
        logger.warning(f"{failed_utils} utility module(s) failed to load.")


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
