"""
Profile Management Helper for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Manage user profiles, preferences, and achievements stored in the database.

Updates:
- Centralized user-related database operations for better modularity and maintainability.
- Enhanced logging for debugging and traceability.
- Integrated and streamlined profile, preference, and achievement management functionalities.
"""

import sys
from loguru import logger
from utils.db_manager import initialize_db_manager

# Metadata
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Streamline user profile, preference, and achievement management via database interactions."

# --- Profile Operations ---
async def create_user_profile(user_id: int, bio: str = "", avatar_url: str = "", preferences: dict = None):
    """
    Creates a user profile in the database.

    Args:
        user_id (int): The ID of the user.
        bio (str): The user's bio.
        avatar_url (str): The URL to the user's avatar.
        preferences (dict): JSON-style user preferences.

    Returns:
        bool: True if the profile was created successfully, False otherwise.
    """
    try:
        preferences = preferences or {}
        await db_manager.insert("user_profiles", {
            "user_id": user_id,
            "bio": bio,
            "avatar_url": avatar_url,
            "preferences": preferences
        })
        logger.info(f"Profile created for user_id={user_id}.")
        return True
    except Exception as e:
        logger.error(f"Failed to create profile for user_id={user_id}: {e}")
        return False

async def fetch_user_profile(user_id: int):
    """
    Fetches a user's profile from the database.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict: User profile data or None if not found.
    """
    try:
        profile = await db_manager.fetch_row("user_profiles", {"user_id": user_id})
        logger.info(f"Fetched profile for user_id={user_id}: {profile}")
        return profile
    except Exception as e:
        logger.error(f"Failed to fetch profile for user_id={user_id}: {e}")
        return None

async def update_user_bio(user_id: int, bio: str):
    """
    Updates a user's bio in the database.

    Args:
        user_id (int): The ID of the user.
        bio (str): The new bio.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        await db_manager.update("user_profiles", {"bio": bio}, {"user_id": user_id})
        logger.info(f"Updated bio for user_id={user_id}: {bio}")
        return True
    except Exception as e:
        logger.error(f"Failed to update bio for user_id={user_id}: {e}")
        return False

# --- Preference Operations ---
async def fetch_user_preferences(user_id: int):
    """
    Fetches a user's preferences from the database.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict: User preferences or None if not found.
    """
    try:
        preferences = await db_manager.fetch_row("user_preferences", {"user_id": user_id})
        logger.info(f"Fetched preferences for user_id={user_id}: {preferences}")
        return preferences
    except Exception as e:
        logger.error(f"Failed to fetch preferences for user_id={user_id}: {e}")
        return None

async def update_user_preference(user_id: int, setting_key: str, setting_value: str):
    """
    Updates a user's preference in the database.

    Args:
        user_id (int): The ID of the user.
        setting_key (str): The preference key to update.
        setting_value (str): The new value for the preference.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        await db_manager.update(
            "user_preferences",
            {"setting_key": setting_key, "setting_value": setting_value},
            {"user_id": user_id},
        )
        logger.info(f"Updated preference for user_id={user_id}: {setting_key}={setting_value}")
        return True
    except Exception as e:
        logger.error(f"Failed to update preference for user_id={user_id}: {e}")
        return False

# --- Achievement Operations ---
async def fetch_user_achievements(user_id: int):
    """
    Fetches a user's achievements from the database.

    Args:
        user_id (int): The ID of the user.

    Returns:
        list: List of achievements or an empty list if none found.
    """
    try:
        achievements = await db_manager.fetch("user_achievements", {"user_id": user_id})
        logger.info(f"Fetched achievements for user_id={user_id}: {achievements}")
        return achievements
    except Exception as e:
        logger.error(f"Failed to fetch achievements for user_id={user_id}: {e}")
        return []

# --- Utility Functions ---
async def does_user_exist(user_id: int):
    """
    Checks if a user exists in the database.

    Args:
        user_id (int): The ID of the user.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    try:
        user = await db_manager.fetch_row("bot_users", {"user_id": user_id})
        exists = user is not None
        logger.info(f"Checked existence for user_id={user_id}: {exists}")
        return exists
    except Exception as e:
        logger.error(f"Failed to check existence for user_id={user_id}: {e}")
        return False

async def setup(*args, **kwargs):
    db_manager = initialize_db_manager(bot)
    pass