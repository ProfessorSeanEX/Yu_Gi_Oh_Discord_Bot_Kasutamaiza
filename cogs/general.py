"""
General commands for Kasutamaiza Bot.

Metadata:
- **Version**: `1.0.0`
- **Author**: `ProfessorSeanEX`
- **Purpose**: Provides essential bot interactions such as ping, uptime, help, and metadata commands.
- **Notes**: Updated to align with helper-based modular structure and enhanced logging standards.
"""

# --- Standard Library Imports ---
# Importing modules for core Python functionality.
import os
import logging
from datetime import datetime, timezone

# --- Third-Party Library Imports ---
# Importing Discord.py and logging libraries for bot interaction and diagnostics.
import discord
from discord.ext import commands
from loguru import logger

# --- Utility Modules ---
# Inject helpers dynamically for modular usage.
from utils import inject_helpers_into_namespace
inject_helpers_into_namespace(globals())  # Dynamically load all known helpers.

# --- Logger Setup ---
# Configure the logger instance specifically for this cog.
logger = logging.getLogger("general_commands")

# --- Metadata for General Cog ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Handles basic bot interactions and utilities."
class General(commands.Cog):
    """
    General commands for the bot, providing essential interactions such as health checks,
    help command access, and metadata display.

    Attributes:
        bot (discord.Bot): The instance of the Discord bot.
        guild_id (int): The ID of the guild where the cog operates.
        token (str): The bot's token for authentication.
        start_time (datetime): The UTC time when the cog was initialized.
        category (str): The category name for grouping commands.
    """

    # Class-level metadata
    __version__ = "1.0.0"
    __author__ = "ProfessorSeanEX"
    __description__ = "Handles basic bot interactions and utilities."
    category = "General"  # Explicitly setting the category for grouping commands.
    
    # --- Initialization Block ---
    def __init__(self, bot: discord.Bot, guild_id: Optional[int], token: Optional[str]):
        """
        Initializes the General cog with guild-specific commands.

        Args:
            bot (discord.Bot): The instance of the Discord bot.
            guild_id (Optional[int]): The guild ID for which the cog is configured.
            token (Optional[str]): The token used for bot authentication.

        Raises:
            ValueError: If `guild_id` or `token` are invalid.
        """
        # Fetch environment variables dynamically using helper functions.
        required_vars = {"GUILD_ID": int, "BOT_TOKEN": str}  # Define required environment variables with expected types.
        env_vars = validate_required_environment_variables(required_vars)  # Validate and fetch environment variables.

        # Assign instance variables with environment values or provided arguments.
        self.guild_id = guild_id or env_vars["GUILD_ID"]  # Use provided guild ID or fallback to environment value.
        self.token = token or env_vars["BOT_TOKEN"]  # Use provided token or fallback to environment value.

        # Assign bot instance and initialize start time.
        self.bot = bot  # Assign the bot instance to the cog.
        self.start_time = datetime.now(timezone.utc)  # Record the UTC initialization time.

        # Register commands and validate their categories for this cog.
        for cmd in self.__cog_commands__:
            log_command_registration(cmd, self.__class__.__name__, self.category)

        # Log the successful initialization of this cog.
        log_custom("DEBUG", f"Initializing {self.__class__.__name__} cog with guild_id={self.guild_id}.")

        log_custom("DEBUG", f"{self.__class__.__name__} cog initialized with guild_id={self.guild_id}.")

    async def calculate_uptime(self) -> str:
        """
        Calculates the bot's uptime since initialization.

        Returns:
            str: Formatted uptime string.
        """
        return format_uptime(self.start_time)

    # --- Section: Ping Command ---
    @discord.slash_command(name="ping", description="Check if the bot is online and view latency.")
    async def slash_ping(self, ctx: discord.ApplicationContext):
        """
        Slash command to check if the bot is online and display latency.

        Args:
            ctx (discord.ApplicationContext): The context of the command execution.
        """
        # Log command execution.
        log_command(ctx, "ping")

        # Validate bot permissions for the command context.
        permissions = validate_permissions(ctx, ["send_messages"])
        log_custom("DEBUG", f"Ping command permissions check: {permissions}")

        # Handle missing permissions.
        if not permissions["has_all"]:
            log_custom("WARNING", f"Missing permissions for Ping command: {permissions['missing']}")
            await respond_permission_denied(ctx, permissions["missing"])
            return

        # Calculate bot latency in milliseconds.
        latency = round(self.bot.latency * 1000)
        log_custom("INFO", f"Bot latency calculated: {latency} ms")

        # Format and send response as an embed.
        fields = {"Latency": f"{latency} ms"}
        await respond_with_embed(
            ctx,
            title="Pong!",
            fields=fields,
            color=discord.Color.green(),
        )
        log_custom("INFO", "Ping response sent successfully.")

    # --- Section: Help Command ---
    @discord.slash_command(name="help", description="Display the help message.")
    async def slash_help(self, ctx: discord.ApplicationContext):
        """
        Displays a dynamic help message with all available commands organized by category.

        Args:
            ctx (discord.ApplicationContext): The command context.
        """
        # Log the execution of the help command for auditing.
        log_command(ctx, "help")

        try:
            # Validate permissions for sending messages in the channel.
            permissions = validate_permissions(ctx, ["send_messages"])
            log_custom("DEBUG", f"Help command permissions check: {permissions}")

            # Handle cases where the bot lacks required permissions.
            if not permissions["has_all"]:
                log_custom("WARNING", f"Missing permissions for Help command: {permissions['missing']}")
                await respond_permission_denied(ctx, permissions["missing"])
                return

            # Prepare a quick-start guide and add environment-configured support links.
            support_url = fetch_environment_variable("SUPPORT_SERVER_URL", str, "Not Configured")
            help_fields = {
                "Quick Start": (
                    f"Use `/ping` to check if the bot is online.\n"
                    f"Use `/help` to see all commands.\n"
                    f"Use `/card_lookup` to find Yu-Gi-Oh! cards.\n"
                    f"[Support Server]({support_url})" if support_url != "Not Configured" else ""
                )
            }

            # Categorize commands by their respective groups.
            categories = categorize_commands(self.bot, group_by="category")
            for category, commands in categories.items():
                help_fields[f"{category} Commands"] = "\n".join(commands)  # Add categorized commands to the help fields.

            # Check if the help message requires pagination based on field size.
            if len(help_fields) > 25 or any(len(value) > 1024 for value in help_fields.values()):
                log_custom("INFO", "Help message requires pagination due to size.")

                # Paginate fields into embeds for large help messages.
                paginated_embeds = paginate_embeds(
                    title="Kasutamaiza Bot Help",
                    fields=help_fields,
                    color=discord.Color.blue()
                )
                await paginate_text(ctx, paginated_embeds, title="Paginated Help Message")
            else:
                # Send a single embed for smaller help messages.
                await respond_with_embed(
                    ctx,
                    title="Kasutamaiza Bot Help",
                    fields=help_fields,
                    color=discord.Color.blue(),
                    ephemeral=False
                )
                log_custom("INFO", "Help message sent successfully.")
        except Exception as e:
            # Handle unexpected errors during the execution of the help command.
            log_error("slash_help", e)
            await respond_with_error(
                ctx,
                title="Error",
                description="An unexpected error occurred while processing your request."
            )
    
    # --- Section: Uptime Command ---
    @discord.slash_command(name="uptime", description="Display the bot's uptime.")
    async def slash_uptime(self, ctx: discord.ApplicationContext):
        """
        Displays the bot's uptime since the last restart.

        Args:
            ctx (discord.ApplicationContext): The context of the command execution.
        """
        # Log command execution.
        log_command(ctx, "uptime")

        # Validate bot permissions for the command context.
        permissions = validate_permissions(ctx, ["send_messages"])
        log_custom("DEBUG", f"Uptime command permissions check: {permissions}")

        # Handle missing permissions.
        if not permissions["has_all"]:
            log_custom("WARNING", f"Missing permissions for Uptime command: {permissions['missing']}")
            await respond_permission_denied(ctx, permissions["missing"])
            return

        # Calculate bot uptime.
        uptime = await self.calculate_uptime()
        log_custom("INFO", f"Calculated uptime: {uptime}")

        # Send the uptime response as an embed.
        await respond_with_embed(
            ctx,
            title="Bot Uptime",
            fields={"Uptime": uptime},
            color=discord.Color.blue(),
        )
        log_custom("INFO", "Uptime response sent successfully.")

    # --- Section: Metadata Command ---
    @discord.slash_command(name="bot_metadata", description="Displays detailed metadata about the bot.")
    async def slash_bot_metadata(self, ctx: discord.ApplicationContext):
        """
        Displays detailed metadata about the bot, including version, author information, and uptime.

        Args:
            ctx (discord.ApplicationContext): The command context.
        """
        # Log command execution for auditing purposes.
        log_command(ctx, "bot_metadata")

        # Validate permissions for sending messages in the channel.
        permissions = validate_permissions(ctx, ["send_messages"])
        log_custom("DEBUG", f"Bot metadata permissions check: {permissions}")

        # Handle missing permissions for the metadata command.
        if not permissions["has_all"]:
            log_custom("WARNING", f"Missing permissions for Bot Metadata command: {permissions['missing']}")
            await respond_permission_denied(ctx, permissions["missing"])
            return

        # Fetch additional metadata from environment variables.
        api_status = fetch_environment_variable("API_ENABLED", bool, False)  # Check if API integration is enabled.
        uptime = format_uptime(self.start_time)  # Calculate bot uptime.

        # Construct metadata fields using helper function and additional data.
        fields = build_metadata(bot=self.bot, version=self.__version__, author=self.__author__, uptime=uptime)
        fields["API Status"] = "Enabled" if api_status else "Disabled"  # Include API status in metadata fields.

        # Send metadata response as an embed.
        await respond_with_embed(
            ctx,
            title="Bot Metadata",
            fields=fields,
            color=discord.Color.blue(),
        )
        log_custom("INFO", "Metadata response sent successfully.")


# --- Setup Function ---
async def setup(bot: discord.Bot, guild_id: Optional[int] = None, token: Optional[str] = None):
    """
    Sets up the General cog by adding it to the bot.

    Args:
        bot (discord.Bot): The bot instance.
        guild_id (Optional[int]): The guild ID, defaulting to the environment variable if not provided.
        token (Optional[str]): The bot token, defaulting to the environment variable if not provided.
    """
    log_custom("DEBUG", "Initializing setup for General cog...")

    # Validate and fetch environment variables dynamically using the helper.
    required_vars = {"GUILD_ID": int, "BOT_TOKEN": str}
    try:
        env_vars = validate_required_environment_variables(required_vars)
        guild_id = guild_id or env_vars["GUILD_ID"]
        token = token or env_vars["BOT_TOKEN"]
    except RuntimeError as e:
        log_error("Environment Validation", e)
        return  # Abort setup if environment validation fails.

    # Add the cog to the bot instance.
    try:
        cog = General(bot, guild_id, token)
        bot.add_cog(cog)
        log_custom("INFO", f"General cog successfully loaded for guild {guild_id}.")
        log_custom("INFO", f"Metadata: Version={General.__version__}, Author={General.__author__}")

        # Log all registered commands for this cog.
        log_registered_commands(bot)

        # Skip sync_commands during setup; defer to on_ready.
        log_custom("DEBUG", "Skipping sync_commands during setup. Will be handled in on_ready.")
    except Exception as e:
        log_error("General Cog Setup", e)
