"""
Command Management Helper Functions for Kasutamaiza Bot.
- Provides utilities for managing and retrieving commands dynamically.

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX
- Purpose: Streamline command management and validation processes for enhanced modularity and scalability.

Notes:
    - Version reset to v1.0.0 as per project phase requirements.
"""

# --- Standard Library Imports ---
# Importing necessary modules for type hints, date manipulation, logging, and Discord bot functionality.
from typing import List, Dict
import logging

# --- Third-Party Library Imports ---
# Importing Discord-specific modules and logging utilities.
import discord
from loguru import logger

# --- Metadata for the file ---
# Metadata defines version, author, and purpose for easy tracking and debugging.
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Streamline command management and validation processes for enhanced modularity and scalability."

# Initialize a logger specifically for this helper module.
# This ensures logs from helpers are easy to identify in debugging.
logger = logging.getLogger("command_management_helper")

# --- Command Formatting Functions ---
def format_command(cmd: discord.SlashCommand) -> str:
    """
    Formats a command for display.

    Args:
        cmd (discord.SlashCommand): The command object.

    Returns:
        str: A formatted string containing the command name and description.

    Example:
        cmd = discord.SlashCommand(name="example", description="An example command")
        format_command(cmd)  # Output: "- `/example`: An example command"
    """
    # Format the command name and description into a display-ready string.
    return f"- `/{cmd.name}`: {cmd.description}"

def validate_command_decorators(bot: discord.Bot):
    """
    Validates that all commands in the bot's cogs are properly decorated as SlashCommands.

    Logs warnings for commands without proper decorators.

    Args:
        bot (discord.Bot): The bot instance.

    Example:
        validate_command_decorators(bot)  # Logs warnings for improperly decorated commands.
    """
    logger.debug("Validating command decorators across all cogs...")
    try:
        # Iterate through all cogs and their commands to validate decorators.
        for cog_name, cog in bot.cogs.items():
            for cmd in cog.walk_commands():
                if not isinstance(cmd, discord.SlashCommand):
                    logger.warning(
                        f"Command '{cmd.name}' in cog '{cog_name}' is not a SlashCommand. "
                        "Check decorators to ensure proper configuration."
                    )
        logger.info("Command decorator validation completed.")
    except Exception as e:
        # Log an error with detailed context if validation fails.
        logger.error(f"Error during command decorator validation: {e}")

# --- Command Categorization Functions ---
def get_commands_by_category(bot: discord.Bot, category_name: str) -> str:
    """
    Fetches commands dynamically by category name.

    Args:
        bot (discord.Bot): The bot instance.
        category_name (str): The name of the category.

    Returns:
        str: A formatted string of commands in the specified category.

    Example:
        get_commands_by_category(bot, "Utilities")
        # Output:
        # "- `/help`: Display the help menu\n- `/info`: Show bot information"
    """
    logger.debug(f"Fetching commands for category: {category_name}")
    try:
        # Filter commands by the specified category attribute in their cogs.
        commands_list = [
            format_command(cmd)
            for cmd in bot.application_commands
            if hasattr(cmd.cog, "category") and cmd.cog.category == category_name
        ]
        # Log and return the list of commands found in the category.
        if commands_list:
            logger.info(f"Commands found in category '{category_name}': {len(commands_list)} commands.")
            return "\n".join(commands_list)
        else:
            logger.warning(f"No commands available in category '{category_name}'.")
            return "No commands available."
    except Exception as e:
        # Log an error and provide a fallback message for failures.
        logger.error(f"Error fetching commands for category '{category_name}': {e}")
        return "Error retrieving commands."

def categorize_commands(bot: discord.Bot, group_by: str = "category") -> Dict[str, List[str]]:
    """
    Categorizes commands based on the specified grouping criteria.

    Args:
        bot (discord.Bot): The bot instance.
        group_by (str): The attribute to group commands by. Default is 'category'.

    Returns:
        Dict[str, List[str]]: A dictionary with category names as keys and command names as values.

    Example:
        categorize_commands(bot)
        # Output:
        # {
        #     "Utilities": ["- `/help`: Display the help menu", "- `/info`: Show bot information"],
        #     "Uncategorized": ["- `/ping`: Check bot latency"]
        # }
    """
    logger.debug(f"Categorizing commands using group_by='{group_by}'")
    categories = {}

    # Iterate through all application commands and group them by the specified attribute.
    for cmd in bot.application_commands:
        cog = cmd.cog
        if cog:
            category_name = getattr(cog, group_by, "Uncategorized")
        else:
            category_name = "Uncategorized"
            logger.warning(
                f"Command '{cmd.name}' is not associated with any cog. Defaulting to 'Uncategorized'."
            )

        categories.setdefault(category_name, []).append(f"- `/{cmd.name}`: {cmd.description}")

    logger.info(f"Categorized commands into {len(categories)} groups.")
    return categories

# --- Command Utility Functions ---
def assign_guild_ids(commands, guild_id):
    """
    Assigns a guild ID to a list of commands dynamically.

    Args:
        commands (list): List of commands to assign the guild ID.
        guild_id (int): The guild ID to assign.

    Example:
        assign_guild_ids([cmd1, cmd2], 123456789)
        # Assigns guild ID 123456789 to the given commands.
    """
    # Iterate through commands and assign the provided guild ID.
    for cmd in commands:
        if isinstance(cmd, discord.SlashCommand):
            cmd.guild_ids = [guild_id]
            logger.debug(f"Assigned guild ID {guild_id} to command: {cmd.name}")

# --- Setup Function ---
async def setup(*args, **kwargs):
    """
    Setup function for initializing the Command Management Helper module.

    Logs metadata and confirms setup is complete.

    Args:
        bot (discord.Bot): The bot instance.

    Raises:
        Exception: If setup fails.

    Example:
        await setup(bot)
    """
    try:
        # Log the beginning of the setup process.
        logger.info("Setting up Command Management Helper module...")

        # Log that setup was completed successfully, along with the module's metadata.
        logger.info(f"Command Management Helper module setup completed. Metadata: Version={__version__}, Author={__author__}")
    except Exception as e:
        # Log any errors encountered during the setup process.
        logger.error(f"Error during setup: {e}")
