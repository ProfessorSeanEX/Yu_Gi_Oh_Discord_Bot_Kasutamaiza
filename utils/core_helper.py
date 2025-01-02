"""
Core Helper functions for Kasutamaiza Bot.
- Provides reusable utility functions for various parts of the bot.

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX
- Purpose: Consolidate utility functions for efficient bot operations across cogs and modules.

Notes:
- Version reset to v1.0.0 as per project phase requirements.
"""

# --- Standard Library Imports ---
# Importing necessary modules for type hints, date manipulation, logging, and Discord bot functionality.
from typing import List, Any
from datetime import datetime, timezone
import logging
import discord

# --- Metadata for the file ---
# Metadata defines version, author, and purpose for easy tracking and debugging.
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Provide reusable utility functions to assist in bot operations across modules."

# Initialize a logger specifically for this helper module.
# This ensures logs from helpers are easy to identify in debugging.
logger = logging.getLogger("core_helper")

# --- Core Bot Metadata Helpers ---
def build_metadata(bot: discord.Bot, version: str, author: str, uptime: str) -> dict:
    """
    Constructs metadata fields for the bot, useful for debugging or informational embeds.

    Args:
        bot (discord.Bot): The bot instance, representing the running bot.
        version (str): Current version of the bot (e.g., '1.0.0').
        author (str): Name of the bot's creator or maintainer.
        uptime (str): Uptime string showing how long the bot has been active.

    Returns:
        dict: A dictionary containing key bot information, formatted for use in embeds or logs.

    Updates:
        - Added fallback values for cases where bot attributes are unavailable.
        - Enhanced logging for better debugging.
    """
    try:
        # Safely gather bot metadata with fallbacks.
        fields = {
            "Name": getattr(bot.user, "name", "Unknown Bot"),
            "ID": str(getattr(bot.user, "id", "Unknown ID")),
            "Version": version,
            "Author": author,
            "Uptime": uptime,
        }
        # Log success for debugging or auditing.
        logger.debug(f"Metadata fields constructed successfully: {fields}")
        return fields
    except Exception as e:
        # Log any errors during metadata construction and return an error message.
        logger.error(f"Error in build_metadata: {e}. Inputs - version: {version}, author: {author}, uptime: {uptime}")
        return {"Error": "Failed to construct metadata fields"}

# --- Time and Formatting Helpers ---
def format_time_ago(timestamp: datetime) -> str:
    """
    Converts a timestamp into a human-readable "time ago" format, useful for logs or embeds.

    Args:
        timestamp (datetime): The timestamp to calculate from.

    Returns:
        str: Human-readable string like "5 minutes ago" or "2 days ago".
    """
    try:
        # Calculate the time difference between now and the given timestamp.
        delta = datetime.utcnow() - timestamp

        # Determine the appropriate "time ago" format based on the difference.
        if delta.days > 0:
            result = f"{delta.days} day(s) ago"  # Format for days.
        elif delta.seconds > 3600:
            result = f"{delta.seconds // 3600} hour(s) ago"  # Format for hours.
        elif delta.seconds > 60:
            result = f"{delta.seconds // 60} minute(s) ago"  # Format for minutes.
        else:
            result = "Just now"  # Format for seconds.
        
        # Log the result for debugging purposes.
        logger.debug(f"Formatted time ago: {result} for timestamp {timestamp}")
        return result
    except Exception as e:
        # Log the error and return a fallback message.
        logger.error(f"Error in format_time_ago: {e}. Input: {timestamp}")
        return "Unknown time"

def format_uptime(start_time: datetime) -> str:
    """
    Calculates and formats the bot's uptime as a string.

    Args:
        start_time (datetime): The start time to calculate uptime from.

    Returns:
        str: Uptime in "X days, HH:MM:SS" format.
    """
    try:
        # Ensure 'now' and 'start_time' are timezone-aware.
        now = datetime.now(timezone.utc)
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        # Calculate the uptime by subtracting start_time from now.
        uptime = now - start_time

        # Convert uptime to a string and remove microseconds for cleaner display.
        result = str(uptime).split(".")[0]
        
        # Log the uptime calculation.
        logger.debug(f"Formatted uptime: {result} for start time {start_time}")
        return result
    except Exception as e:
        # Log any errors and return a fallback message.
        logger.error(f"Error in format_uptime: {e}. Input: {start_time}")
        return "Unknown uptime"

# --- String and List Helpers ---
def split_long_string(text: str, limit: int = 1024) -> List[str]:
    """
    Splits a long string into smaller chunks to fit Discord message limits or similar constraints.

    Args:
        text (str): The input string.
        limit (int): Maximum length of each chunk. Default is 1024.

    Returns:
        List[str]: List of string chunks, or an empty list if input is empty.
    """
    if not text:  # Check if the input text is empty or None.
        logger.debug("Empty or None text input for split_long_string.")
        return []  # Return an empty list if there's no text to split.

    # Use a list comprehension to divide the string into chunks of 'limit' size.
    return [text[i:i + limit] for i in range(0, len(text), limit)]

def truncate_string(text: str, limit: int = 1024, suffix: str = "...") -> str:
    """
    Truncates a string to a specified length and appends a suffix if truncated.

    Args:
        text (str): The input string.
        limit (int): Maximum allowed length of the string.
        suffix (str): Suffix to append when truncation occurs.

    Returns:
        str: Truncated string or the original string if within the limit.
    """
    if not text:  # Check if the input text is empty or None.
        logger.debug("Empty or None text input for truncate_string.")
        return suffix  # Return only the suffix if no valid text is provided.

    # If the string length is within the limit, return it unchanged.
    # Otherwise, truncate and append the suffix.
    return text if len(text) <= limit else text[:limit - len(suffix)] + suffix

def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Divides a list into smaller chunks of a specified size.

    Args:
        data (List[Any]): The list to split.
        chunk_size (int): Number of elements per chunk.

    Returns:
        List[List[Any]]: List of smaller lists.
    """
    # Use a list comprehension to create chunks of size 'chunk_size'.
    # This works by iterating over the list in steps of 'chunk_size'.
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

# --- Validation Helpers ---
def validate_number_range(value: int, min_val: int, max_val: int) -> bool:
    """
    Validates if a number falls within a specified range.

    Args:
        value (int): The number to validate.
        min_val (int): Minimum allowable value.
        max_val (int): Maximum allowable value.

    Returns:
        bool: True if the value is within range, otherwise False.
    """
    try:
        # Check if the number 'value' falls between 'min_val' and 'max_val' (inclusive).
        result = min_val <= value <= max_val

        # Log the validation results for debugging purposes.
        logger.debug(f"Validating range: Value={value}, Min={min_val}, Max={max_val}, Result={result}")
        return result
    except Exception as e:
        # Log any errors encountered during validation and return False as a fallback.
        logger.error(f"Error in validate_number_range: {e}. Inputs - value: {value}, min_val: {min_val}, max_val: {max_val}")
        return False

# --- Setup Function ---
async def setup(*args, **kwargs):
    """
    Setup function for initializing the helper module.

    Logs metadata and confirms setup is complete.
    """
    try:
        # Log the beginning of the setup process.
        logger.info("Setting up Core Helper module...")

        # Log that setup was completed successfully, along with the module's metadata.
        logger.info(f"Core Helper module setup completed. Metadata: Version={__version__}, Author={__author__}")
    except Exception as e:
        # Log any errors encountered during the setup process.
        logger.error(f"Error during setup: {e}")
