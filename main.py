"""
Main entry point for the Kasutamaiza Bot.
- Initializes the bot, performs permissions checks, loads modules, and ensures commands sync properly with enhanced debugging.

Metadata:
- Version: 1.0.0          # Indicates the current version of the bot's main entry point.
- Author: ProfessorSeanEX  # The developer or maintainer of this script.
- Purpose: Initializes and runs the Kasutamaiza Bot with enhanced debugging and modularity.

Notes:
- Refactored to integrate standardized helper functions and logging utilities.
"""

# --- Standard Library Imports ---
import os # For environment variable management.
import sys  # To manipulate the Python runtime environment and paths.
from pathlib import Path  # To handle filesystem paths in a cross-platform way.
import signal  # For handling termination signals (e.g., SIGINT).
import asyncio  # To manage asynchronous tasks and events.
from datetime import datetime, timezone  # For handling time-related operations.
import importlib
import asyncpg

# --- Third-Party Library Imports ---
import discord # Discord API integration for bot functionality.

# --- Project Imports ---
from utils import inject_helpers_into_namespace # Inject helpers dynamically.

# Inject all helpers into the global namespace for ease of use.
inject_helpers_into_namespace(globals())  # Dynamically inject helper functions.

# --- Metadata ---
__version__ = "1.0.0"  # Current version of the bot's main script.
__author__ = "ProfessorSeanEX"  # Developer responsible for maintaining this script.
__purpose__ = "Initialize and run the Kasutamaiza Bot with enhanced debugging and modularity."

# --- Directories ---
BASE_DIR = Path(__file__).resolve().parent  # Root directory of the script.
COGS_DIR = validate_directory(BASE_DIR / "cogs")  # Validate and set directory for bot cogs.
UTILS_DIR = validate_directory(BASE_DIR / "utils")  # Validate and set directory for utility functions.
LOG_DIR = validate_directory(BASE_DIR / "logs")  # Validate and set directory for storing log files.

# Ensure required directories exist.
LOG_DIR.mkdir(parents=True, exist_ok=True)  # Create log directory if it doesn't exist.

# --- Load Environment Variables ---
try:
    required_vars = {"BOT_TOKEN": str, "GUILD_ID": int}
    env_vars = validate_required_environment_variables(required_vars)  # Validate and fetch environment variables.
    TOKEN = env_vars["BOT_TOKEN"]  # Discord bot token.
    GUILD_ID = env_vars["GUILD_ID"]  # Primary guild (server) ID for bot operations.
except RuntimeError as e:
    log_error("Environment Variable Validation", e)
    exit(1)  # Exit if environment validation fails.

# --- Logging Setup ---
log_custom("INFO", "Initializing Kasutamaiza Bot logging...")  # Start of logging setup.
log_custom("DEBUG", f"Base Directory: {BASE_DIR}")
log_custom("DEBUG", f"Log Directory: {LOG_DIR}")

# --- Bot Setup ---
# Define bot intents to control which events the bot listens to.
intents = discord.Intents.default()  # Use default intents as a baseline.
intents.message_content = True  # Enable message content access for command parsing.
intents.members = True  # Enable access to guild (server) member data.

# Initialize the bot with the specified intents and guilds.
bot = discord.Bot(intents=intents, guilds=[discord.Object(id=GUILD_ID)])

# Add custom bot attributes for modularity and feature tracking.
bot.muted_members = {}  # Dictionary to track muted members by guild.
bot.start_time = None  # Timestamp for bot's start time (used for uptime calculations).
bot.db_pool = None  # Placeholder for the bot's database connection pool.

# --- Event Handlers ---
@bot.event
async def on_ready():
    """
    Event triggered when the bot is ready and connected to Discord.

    This function performs the following tasks:
    - Logs the bot's readiness status and connected guilds.
    - Logs sanitized environment variables for debugging.
    - Initializes the database manager, connection pool, and table schemas.
    - Handles errors gracefully during initialization.
    """
    try:
        # Log basic bot status.
        log_command(bot, "on_ready")
        log_custom("INFO", f"Bot online as {bot.user}.")
        log_custom("DEBUG", f"Connected to Guilds: {[guild.name for guild in bot.guilds]}.")

        # Sanitize and log environment variables.
        sensitive_keys = {"BOT_TOKEN", "DB_PASSWORD"}
        sanitized_env_vars = {
            k: ("[REDACTED]" if k in sensitive_keys else v) for k, v in os.environ.items()
        }
        log_custom("DEBUG", f"Environment Variables: {sanitized_env_vars}")

        # Database Initialization
        try:
            if not hasattr(bot, "db_manager"):
                log_custom("INFO", "Initializing DatabaseManager...")
                env_vars = validate_required_environment_variables({
                    "DB_HOST": str,
                    "DB_PORT": int,
                    "DB_USER": str,
                    "DB_PASSWORD": str,
                    "DB_NAME": str,
                })
                db_manager = initialize_db_manager(bot, env_vars)
                bot.db_manager = db_manager

            if not hasattr(bot, "db_pool") or not bot.db_pool:
                log_custom("INFO", "Initializing database connection pool...")
                bot.db_pool = await bot.db_manager.initialize_pool()

            log_custom("INFO", "Validating and creating database schemas...")
            await bot.db_manager.ensure_table_schemas()

            log_custom("INFO", "Database initialized successfully.")
        except asyncpg.PostgresError as pg_error:
            log_error(f"PostgreSQL Error during Database Initialization: {str(pg_error)}")
            await bot.close()
            exit(1)
        except RuntimeError as re:
            log_error(f"Database Initialization Error: {str(re)}")
            await bot.close()
            exit(1)
        except Exception as e:
            log_error("Unexpected Error during Database Initialization", e)
            await bot.close()
            exit(1)


        # Validate bot permissions in the primary guild.
        try:
            guild = bot.get_guild(GUILD_ID)
            if guild:
                bot_member = guild.me
                permissions = validate_bot_permissions(
                    bot_member,
                    [
                        "administrator",
                        "manage_guild",
                        "manage_roles",
                        "send_messages",
                        "manage_messages",
                        "read_message_history",
                        "manage_channels",
                    ],
                )
                if not permissions["has_all"]:
                    log_custom("WARNING", f"Missing permissions: {permissions['missing']}")
                else:
                    log_custom("INFO", "Bot has all required permissions.")
    
        except Exception as e:
            log_error("Permission Validation", e)

        # Load cogs and utilities dynamically.
        try:
            load_results = await asyncio.gather(
                load_modules_from_directory(str(COGS_DIR), "cogs", bot),
                load_modules_from_directory(str(UTILS_DIR), "utils", bot),
            )
            log_custom("INFO", f"Modules loaded successfully: {load_results}")
        except Exception as e:
            log_error("Module Loading", e)

        # Validate command decorators for all loaded commands.
        validate_command_decorators(bot)  # Use helper for validation.

        # Sync commands with Discord.
        try:
            synced = await bot.sync_commands(guild_ids=[GUILD_ID])
            if synced is None:
                log_custom("WARNING", "No commands were synchronized.")
                synced = []

            log_custom("INFO", f"Commands synchronized: {[cmd.name for cmd in synced]}")
        except Exception as e:
            log_error("Command Synchronization", e)

        bot.start_time = datetime.now(timezone.utc)  # Set the bot's start time.
        log_uptime(bot.start_time)  # Log uptime details.
    
    except Exception as e:
        log_error("on_ready", e)

# --- Graceful Shutdown ---
async def handle_graceful_shutdown(bot, db_manager):
    """
    Handles signals for graceful shutdown using the Shutdown Helper.

    Args:
        bot: The bot instance.
        db_manager: The database manager instance.
    """
    try:
        log_custom("INFO", "Shutting down Kasutamaiza Bot...")
        if db_manager:
            await db_manager.close_pool()
        await shutdown_procedure(db_manager=db_manager)
        log_custom("INFO", "Shutdown complete.")
    except Exception as e:
        log_error("Graceful Shutdown", e)
    finally:
        await close_bot()


# --- Main Execution ---
if __name__ == "__main__":
    try:
        async def shutdown_coroutine():
            await handle_graceful_shutdown(bot, bot.db_manager)

        setup_signal_handlers()  # Configure signal handlers.
        log_custom("INFO", "Starting Kasutamaiza Bot...")
        bot.run(TOKEN)
    except Exception as e:
        log_error("Bot Startup", e)
