"""
Debug commands for Kasutamaiza Bot.
- Tools for diagnostics, permission checking, and health monitoring.

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX
- Purpose: Provides bot diagnostics, permission checking, and health monitoring tools with enhanced validation.
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
class Debug(commands.Cog):
    """
    Debugging and diagnostic commands for the bot.
    Includes permission checking, diagnostics, and health tools.
    """

    # Class-level metadata
    __version__ = "1.0.0"
    __author__ = "ProfessorSeanEX"
    __description__ = "Provides tools for bot diagnostics, permission checking, and health monitoring."
    category = "Debug"

    def __init__(self, bot, guild_id, token):
        """
        Initializes the Debug cog with guild-specific commands.
        """
        if not guild_id or not token:
            raise ValueError("guild_id and token must be provided for Debug cog initialization.")

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
        
    # --- Section: Environment Variables Command ---
    @discord.slash_command(name="env_variables", description="Display all environment variables.")
    async def env_variables(self, ctx: discord.ApplicationContext):
        """
        Command to display all loaded environment variables, restricted to specific users.

        Args:
            ctx (discord.ApplicationContext): The context of the command execution.

        Behavior:
            - Validates the user executing the command using a predefined user ID.
            - Fetches and paginates environment variables, excluding sensitive values.
            - Sends the response as ephemeral messages to ensure privacy.

        Raises:
            Exception: Logs and responds to any unexpected errors during execution.
        """
        # Log command execution for auditing purposes.
        log_command(ctx, "env_variables")

        # Define the authorized user ID for command execution.
        allowed_user_id = 194141500211200002  # Replace with your Discord user ID.

        # Restrict access to the command.
        if ctx.user.id != allowed_user_id:
            log_custom(
                "WARNING",
                f"Unauthorized access attempt to env_variables by user {ctx.user} (ID: {ctx.user.id})"
            )
            await respond_with_error(
                ctx,
                title="Access Denied",
                description="You do not have permission to execute this command.",
                ephemeral=True
            )
            return

        try:
            # Fetch environment variables while obscuring sensitive values.
            sensitive_keys = {"BOT_TOKEN", "DATABASE_PASSWORD"}  # Add sensitive keys to this set.
            env_vars = {
                key: ("[REDACTED]" if key in sensitive_keys else os.getenv(key, "Not Set"))
                for key in os.environ.keys()
            }

            # Paginate the dictionary into manageable chunks for embeds.
            paginated_envs = paginate_dict(env_vars)

            # Send paginated embeds for each chunk.
            for chunk in paginated_envs:
                await respond_with_embed(
                    ctx,
                    title="Environment Variables",
                    fields=chunk,
                    color=discord.Color.blue(),
                    ephemeral=True
                )

            # Log successful execution for auditing purposes.
            log_custom("INFO", f"Environment variables displayed successfully for {ctx.user}.")

        except Exception as e:
            # Log the error and send an error response to the user.
            log_error("env_variables", e)
            await respond_with_error(
                ctx,
                title="Error",
                description="An unexpected error occurred while retrieving environment variables.",
            )

    @discord.slash_command(name="diagnostics", description="Get full bot diagnostics and recent error logs.")
    async def slash_diagnostics(self, ctx: discord.ApplicationContext):
        logger.info(f"Diagnostics command triggered by {ctx.user}")
        await ctx.defer(ephemeral=True)

        permissions = validate_permissions(ctx, ["administrator", "manage_guild", "manage_roles"])
        if not permissions["has_all"]:
            await format_embed_response(ctx, title="Permission Denied", fields={"Missing Permissions": ", ".join(permissions["missing"])}, color=discord.Color.red(), ephemeral=True)
            return

        uptime = await self.calculate_uptime()
        categories = categorize_commands(self.bot, group_by="cog")
        categorized_commands = {f"{category} Commands": "\n".join(commands) for category, commands in categories.items()}
        perms = ctx.guild.me.guild_permissions
        permissions_info = summarize_permissions(perms, required_permissions=[
            "administrator", "manage_guild", "manage_roles", "send_messages", "manage_messages", "read_message_history", "manage_channels"
        ])
        loaded_cogs = "\n".join(f"- {cog}" for cog in self.bot.cogs.keys())
        environment_info = [
            "✅ `BOT_TOKEN` is set." if self.token else "❌ `BOT_TOKEN` is missing.",
            f"✅ `GUILD_ID`: `{self.guild_id}`" if self.guild_id else "❌ `GUILD_ID` is missing or invalid."
        ]

        fields = {
            "Name": self.bot.user.name,
            "ID": self.bot.user.id,
            "Uptime": uptime,
            "Total Commands": len(self.bot.application_commands),
            "Permissions": permissions_info,
            "Loaded Cogs": loaded_cogs,
            "Environment Variables": "\n".join(environment_info),
            **categorized_commands,
        }
        await format_embed_response(ctx, title="Bot Diagnostics", fields=fields, ephemeral=True)

    @discord.slash_command(name="check_permissions", description="Check the bot's permissions in the current channel.")
    async def slash_check_permissions(self, ctx: discord.ApplicationContext):
        permissions = validate_permissions(ctx, ["administrator", "manage_guild", "manage_roles"])
        if not permissions["has_all"]:
            await format_embed_response(ctx, title="Permission Denied", fields={"Missing Permissions": ", ".join(permissions["missing"])}, color=discord.Color.red(), ephemeral=True)
            return

        perms = ctx.channel.permissions_for(ctx.guild.me)
        permissions_info = summarize_permissions(perms, required_permissions=[
            "administrator", "manage_guild", "manage_roles", "send_messages", "manage_messages", "read_message_history", "manage_channels"
        ])
        logger.info(f"Permissions checked in {ctx.guild.name} ({ctx.guild.id}): {permissions_info}")
        await format_embed_response(ctx, title=f"Permissions in {ctx.channel.name}", fields={"Permissions": permissions_info})

    @discord.slash_command(name="log_errors", description="Retrieve recent error logs from the bot.")
    async def slash_log_errors(self, ctx: discord.ApplicationContext, lines: int = 10, full_log: bool = False):
        logger.info(f"Log errors command triggered by {ctx.user}")
        log_file_path = "bot.log"

        try:
            if full_log and os.path.exists(log_file_path):
                logger.info("Sending full log file as a DM.")
                with open(log_file_path, "rb") as log_file:
                    await ctx.user.send(file=discord.File(fp=log_file, filename="bot.log"))
                    await format_embed_response(ctx, title="Full Log Sent", fields={"Message": "The full log has been sent to your DMs."}, ephemeral=True)
            else:
                errors = extract_error_logs(log_file_path, severity="ERROR", lines=lines)
                fields = {"Recent Errors": errors or "No recent errors found in the logs."}
                await format_embed_response(ctx, title="Recent Errors", fields=fields, ephemeral=True)
        except discord.Forbidden:
            logger.error("Unable to send logs via DM. User may have DMs disabled.")
            await format_embed_response(ctx, title="DM Failed", fields={"Message": "Enable DMs to receive the logs."}, color=discord.Color.red(), ephemeral=True)
        except Exception as e:
            logger.error(f"Unexpected error in log_errors command: {e}")
            await format_embed_response(ctx, title="Error", fields={"Message": f"Unexpected error: {str(e)}"}, color=discord.Color.red(), ephemeral=True)


async def setup(bot: discord.Bot, guild_id: Optional[int] = None, token: Optional[str] = None):
    """
    Sets up the Debug cog by adding it to the bot.
    """
    logger.debug("Initializing Debug cog setup...")

    # Fetch environment variables if not explicitly provided
    guild_id = guild_id or int(os.getenv("GUILD_ID", 0))
    token = token or os.getenv("BOT_TOKEN", "")

    # Validate environment variables
    if guild_id == 0 or not token:
        logger.error("GUILD_ID or BOT_TOKEN environment variable is not set or invalid.")
        return

    try:
        # Add cog to the bot
        cog = Debug(bot, guild_id, token)
        bot.add_cog(cog)
        logger.info(f"Debug cog successfully loaded for guild {guild_id}.")
        logger.info(f"Metadata: Version={Debug.__version__}, Author={Debug.__author__}")

        # Do not call sync_commands here; defer to on_ready
        logger.debug("Skipping sync_commands during setup. Will be handled in on_ready.")
    except Exception as e:
        logger.error(f"Failed to setup Debug cog: {e}")

        # Log registered commands after setup
        if bot.application_commands:
            logger.info("Registered commands after Debug cog setup:")
            for cmd in bot.application_commands:
                logger.info(f" - Command: {cmd.name} | Description: {cmd.description} | Guild ID(s): {cmd.guild_ids or 'Global'}")
        else:
            logger.warning("No commands found in bot.application_commands after cog setup.")
    except Exception as e:
        logger.error(f"Failed to setup Debug cog: {e}")
