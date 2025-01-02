# --- Metadata ---
"""
Global Database Manager for Kasutamaiza Bot.

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX
- Purpose: Provide a centralized global manager for DatabaseManager, avoiding circular dependencies.
"""


# --- Imports ---
import discord
import logger
from utils.db_manager import DatabaseManager  # Import DatabaseManager for instantiation.

# --- Metadata[for the file] ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Provide a centralized global manager for DatabaseManager."


# --- Encapsulated Helper: initialize_db_manager ---

def initialize_db_manager(bot, env_vars=None) -> DatabaseManager:
    """
    Initializes and attaches the DatabaseManager to the bot instance.

    Args:
        bot (discord.Bot): The bot instance for context.
        env_vars (dict): Validated environment variables.

    Returns:
        DatabaseManager: The initialized DatabaseManager instance.
    """
    # Check if the DatabaseManager is already initialized in the bot instance
    if hasattr(bot, "db_manager") and bot.db_manager is not None:
        return bot.db_manager

    # Validate environment variables if not provided
    if env_vars is None:
        env_vars = validate_required_environment_variables({
            "DB_HOST": str,
            "DB_PORT": int,
            "DB_USER": str,
            "DB_PASSWORD": str,
            "DB_NAME": str,
        })

    # Create and attach DatabaseManager
    db_manager = DatabaseManager(bot, env_vars)
    bot.db_manager = db_manager
    return db_manager


# --- Setter Function ---
def set_db_manager(manager: DatabaseManager):
    """
    Sets the global DatabaseManager instance.

    Args:
        manager (DatabaseManager): The instance to set globally.

    Notes:
        - Used during initialization to register the `DatabaseManager`.
    """
    global db_manager
    db_manager = manager
    logger.info("Global DatabaseManager instance set.")


# --- Getter Function ---
def get_db_manager() -> DatabaseManager:
    """
    Retrieves the global DatabaseManager instance.

    Returns:
        DatabaseManager: The global DatabaseManager instance.

    Raises:
        RuntimeError: If the DatabaseManager is not initialized.
    """
    if _db_manager is None:
        logger.error("DatabaseManager accessed before initialization.")
        raise RuntimeError("DatabaseManager has not been initialized.")
    return _db_manager
