"""
Utility commands for Kasutamaiza Bot.
- Provides server utilities such as metadata, database interactions, and server statistics.

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX
- Purpose: Provide metadata, server details, and database utilities for enhanced server operations with validation and categorization.
"""

import os
import logging
from datetime import datetime, timezone

# Import modules
import discord
from discord.ext import commands
from loguru import logger
from typing import Optional

# Utility imports
from utils import inject_helpers_into_namespace

# Inject all helpers into this module's global namespace
inject_helpers_into_namespace(globals())

logger = logging.getLogger(__name__)
class Utility(commands.Cog):
    """
    Utility commands for the bot.
    Provides metadata, server details, and other useful utilities.
    """

    # Class-level metadata
    __version__ = "1.0.0"
    __author__ = "ProfessorSeanEX"
    __description__ = "Provides bot-related information, server details, and enhanced database utilities."
    category = "Utility"

    def __init__(self, bot, guild_id, token):
        """
        Initializes the Utility cog with guild-specific commands.
        """
        if not guild_id or not token:
            raise ValueError("guild_id and token must be provided for Utility cog initialization.")

        self.bot = bot
        self.guild_id = guild_id
        self.token = token
        self.start_time = datetime.now(timezone.utc)
        for cmd in self.__cog_commands__:
            logger.debug(f"Registering command '{cmd.name}' to cog '{self.__class__.__name__}' with category '{self.category}'.")

        # Enforce category attribute
        if not hasattr(self, "category") or not isinstance(self.category, str):
            logger.warning(f"Cog '{self.__class__.__name__}' is missing a 'category' attribute. Defaulting to 'Uncategorized'.")
            self.category = "Uncategorized"

        # Assign guild_ids to commands dynamically
        for cmd in self.__cog_commands__:
            if isinstance(cmd, discord.SlashCommand):
                cmd.guild_ids = [self.guild_id]

        # Debugging log for validation
        logger.debug(f"Initializing {self.__class__.__name__} with category: {self.category}")
        logger.debug(f"{self.__class__.__name__} cog initialized with guild_id={self.guild_id}.")

    async def calculate_uptime(self) -> str:
        """
        Calculates the bot's uptime since initialization.

        Returns:
            str: Formatted uptime string.
        """
        uptime = datetime.now(timezone.utc) - self.start_time
        return str(uptime).split(".")[0]


    @discord.slash_command(name="info", description="Provides information about the bot.")
    async def slash_info(self, ctx: discord.ApplicationContext):
        """
        Provides metadata and general information about the bot.
        """
        permissions = validate_permissions(ctx, ["send_messages"])
        if not permissions["has_all"]:
            await format_embed_response(ctx, title="Permission Denied", fields={"Missing Permissions": ", ".join(permissions["missing"])}, color=discord.Color.red(), ephemeral=True)
            return

        log_command(ctx, "info")
        fields = {
            "Version": self.__version__,
            "Author": self.__author__,
            "Purpose": "Enhance your Yu-Gi-Oh experience and server engagement.",
            "Total Commands": len(self.bot.application_commands),
            "Connected Guild": f"{ctx.guild.name} (ID: {ctx.guild.id})"
        }
        await format_embed_response(ctx, title="Kasutamaiza Bot Metadata", fields=fields)

    @discord.slash_command(name="server_info", description="Provides information about the current server.")
    async def slash_server_info(self, ctx: discord.ApplicationContext):
        """
        Provides information about the server.
        """
        permissions = validate_permissions(ctx, ["send_messages"])
        if not permissions["has_all"]:
            await format_embed_response(ctx, title="Permission Denied", fields={"Missing Permissions": ", ".join(permissions["missing"])}, color=discord.Color.red(), ephemeral=True)
            return

        log_command(ctx, "server_info")
        guild = ctx.guild
        fields = {
            "Name": guild.name,
            "ID": guild.id,
            "Owner": str(guild.owner),
            "Members": guild.member_count,
            "Created At": guild.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        await format_embed_response(ctx, title="Server Information", fields=fields)

    @discord.slash_command(name="bot_status", description="Provides the bot's current status.")
    async def slash_bot_status(self, ctx: discord.ApplicationContext):
        """
        Displays the bot's online status and latency.
        """
        permissions = validate_permissions(ctx, ["send_messages"])
        if not permissions["has_all"]:
            await format_embed_response(ctx, title="Permission Denied", fields={"Missing Permissions": ", ".join(permissions["missing"])}, color=discord.Color.red(), ephemeral=True)
            return

        latency = round(self.bot.latency * 1000)  # Convert latency to milliseconds
        log_command(ctx, "bot_status")
        fields = {
            "Status": "Online",
            "Latency": f"{latency}ms"
        }
        await format_embed_response(ctx, title="Bot Status", fields=fields)

    @discord.slash_command(name="view_user", description="View a user's profile in the database.")
    async def slash_view_user(self, ctx: discord.ApplicationContext, user_id: int):
        """
        Fetch and display information about a user from the database.
        """
        permissions = validate_permissions(ctx, ["send_messages"])
        if not permissions["has_all"]:
            await format_embed_response(ctx, title="Permission Denied", fields={"Missing Permissions": ", ".join(permissions["missing"])}, color=discord.Color.red(), ephemeral=True)
            return

        log_command(ctx, "view_user")
        try:
            profile = await fetch_user_profile(user_id)
            if profile:
                fields = {
                    "User ID": profile["user_id"],
                    "Bio": profile["bio"] or "No bio available",
                    "Preferences": profile.get("preferences", "Not set")
                }
                await format_embed_response(ctx, title="User Profile", fields=fields)
            else:
                await format_embed_response(ctx, title="User Not Found", fields={"Error": f"No user found with ID {user_id}"}, color=discord.Color.red(), ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to view user profile: {e}")
            await format_embed_response(ctx, title="Error", fields={"Error": str(e)}, color=discord.Color.red(), ephemeral=True)

    @discord.slash_command(name="update_user_bio", description="Update a user's bio in the database.")
    async def slash_update_user_bio(self, ctx: discord.ApplicationContext, user_id: int, bio: str):
        """
        Update a user's bio in the database.
        """
        permissions = validate_permissions(ctx, ["send_messages"])
        if not permissions["has_all"]:
            await format_embed_response(ctx, title="Permission Denied", fields={"Missing Permissions": ", ".join(permissions["missing"])}, color=discord.Color.red(), ephemeral=True)
            return

        log_command(ctx, "update_user_bio")
        try:
            success = await update_user_bio(user_id, bio)
            if success:
                fields = {"Result": "Bio updated successfully", "User ID": user_id}
                await format_embed_response(ctx, title="Update Successful", fields=fields)
            else:
                await format_embed_response(ctx, title="Update Failed", fields={"Error": "Unable to update bio"}, color=discord.Color.red(), ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to update user bio: {e}")
            await format_embed_response(ctx, title="Error", fields={"Error": str(e)}, color=discord.Color.red(), ephemeral=True)


async def setup(bot: discord.Bot, guild_id: Optional[int] = None, token: Optional[str] = None):
    """
    Sets up the Utility cog by adding it to the bot.
    """
    logger.debug("Initializing Utility cog setup...")

    # Fetch environment variables if not explicitly provided
    guild_id = guild_id or int(os.getenv("GUILD_ID", 0))
    token = token or os.getenv("BOT_TOKEN", "")

    # Validate environment variables
    if guild_id == 0 or not token:
        logger.error("GUILD_ID or BOT_TOKEN environment variable is not set or invalid.")
        return

    try:
        # Add cog to the bot
        cog = Utility(bot, guild_id, token)
        bot.add_cog(cog)
        logger.info(f"Utility cog successfully loaded for guild {guild_id}.")
        logger.info(f"Metadata: Version={Utility.__version__}, Author={Utility.__author__}")

        # Do not call sync_commands here; defer to on_ready
        logger.debug("Skipping sync_commands during setup. Will be handled in on_ready.")
    except Exception as e:
        logger.error(f"Failed to setup Utility cog: {e}")

        # Log registered commands after setup
        if bot.application_commands:
            logger.info("Registered commands after Utility cog setup:")
            for cmd in bot.application_commands:
                logger.info(f" - Command: {cmd.name} | Description: {cmd.description} | Guild ID(s): {cmd.guild_ids or 'Global'}")
        else:
            logger.warning("No commands found in bot.application_commands after cog setup.")

