"""
{COG_NAME} commands for Kasutamaiza Bot.
- Tagline description

Metadata:
- Version: {COG_VERSION}
- Author: {COG_AUTHOR}
- Purpose: {COG_PURPOSE}
"""

# --- Standard Library Imports ---
import os
from datetime import datetime, timezone

# --- Third-Party Library Imports ---
import discord
from discord.ext import commands
from loguru import logger
from typing import Optional

# --- Utility Modules ---
from utils import inject_helpers_into_namespace

# Inject all helpers into this module's global namespace
inject_helpers_into_namespace(globals())

logger = logger.bind(name=__name__)  # Attach cog name to logger for better context


class COG_CLASS(commands.Cog):
    """
    {COG_NAME} commands for managing server operations.

    Provides functionality to enhance and streamline bot interactions within the server.
    """

    # Class-level metadata
    __version__ = "{COG_VERSION}"
    __author__ = "{COG_AUTHOR}"
    __description__ = "{COG_DESCRIPTION}"
    category = "{COG_CATEGORY}"  # Used to categorize commands dynamically

    def __init__(self, bot: discord.Bot, guild_id: int, token: str):
        """
        Initializes the {COG_NAME} cog with guild-specific commands.

        Args:
            bot (discord.Bot): The bot instance.
            guild_id (int): The ID of the guild the cog is attached to.
            token (str): The bot token for API interaction.
        """
        if not guild_id or not token:
            raise ValueError("Both 'guild_id' and 'token' must be provided for cog initialization.")

        self.bot = bot
        self.guild_id = guild_id
        self.token = token
        self.start_time = datetime.now(timezone.utc)

        # Dynamically assign guild_ids to slash commands
        for cmd in self.__cog_commands__:
            if isinstance(cmd, discord.SlashCommand):
                cmd.guild_ids = [self.guild_id]

        logger.info(f"{COG_NAME} cog initialized with guild_id={self.guild_id}.")

    async def calculate_uptime(self) -> str:
        """
        Calculates the bot's uptime since initialization.

        Returns:
            str: Formatted uptime string (HH:MM:SS).
        """
        try:
            uptime = datetime.now(timezone.utc) - self.start_time
            return str(uptime).split(".")[0]  # Format as HH:MM:SS
        except Exception as e:
            logger.error(f"Error calculating uptime: {e}")
            return "Unknown"


async def setup(bot: discord.Bot, guild_id: Optional[int] = None, token: Optional[str] = None):
    """
    Sets up the {COG_NAME} cog by adding it to the bot.

    Args:
        bot (discord.Bot): The bot instance.
        guild_id (Optional[int]): The guild ID for the cog, defaulting to an environment variable if not provided.
        token (Optional[str]): The bot token for the cog, defaulting to an environment variable if not provided.
    """
    logger.debug(f"Initializing {COG_NAME} cog setup...")

    # Fetch and validate environment variables
    required_vars = {"GUILD_ID": int, "BOT_TOKEN": str}
    try:
        env_vars = validate_required_environment_variables(required_vars)
        guild_id = guild_id or env_vars["GUILD_ID"]
        token = token or env_vars["BOT_TOKEN"]
    except RuntimeError as e:
        logger.error(f"Environment variable validation failed for {COG_NAME} cog: {e}")
        return

    # Attempt to add cog to bot
    try:
        cog = COG_CLASS(bot, guild_id, token)
        bot.add_cog(cog)
        logger.info(f"{COG_NAME} cog successfully loaded for guild {guild_id}.")
        logger.info(f"Metadata: Version={COG_CLASS.__version__}, Author={COG_CLASS.__author__}")

        # Log all registered commands for the cog
        log_registered_commands(bot)

        # Note: Do not sync_commands here; defer to on_ready
        logger.debug("Skipping sync_commands during setup. Will be handled in on_ready.")
    except Exception as e:
        logger.error(f"Failed to setup {COG_NAME} cog: {e}")
        log_registered_commands(bot)  # Log commands even if setup fails

