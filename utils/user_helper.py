"""
User Helper for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Centralized utilities for user management, including profiles, preferences, and achievements.

Updates:
- Enhanced utility functions for user profile, preferences, and achievements.
- Improved logging and query handling for clarity and debugging.
- Modular structure with future scalability in mind.
"""

from typing import Optional, List
import asyncpg
from loguru import logger

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Streamline user data management and interactions."

# --- Utility Functions ---
def format_filters(filters: dict) -> str:
    """
    Formats SQL filters for WHERE clauses.

    Args:
        filters (dict): Column-value pairs to use in the filter.

    Returns:
        str: The WHERE clause for SQL.
    """
    return " AND ".join([f"{key} = ${i+1}" for i, key in enumerate(filters.keys())])

def log_database_interaction(query: str, parameters: list):
    """
    Logs database interactions for debugging and auditing.

    Args:
        query (str): The SQL query executed.
        parameters (list): The parameters used in the query.
    """
    param_str = ", ".join(map(str, parameters)) if parameters else "None"
    logger.debug(f"Executing query: {query} | Parameters: {param_str}")

# --- User Profile Management ---
async def fetch_user_profile(connection, user_id: int) -> Optional[dict]:
    """
    Fetches a user's profile from the database.

    Args:
        connection: Database connection.
        user_id (int): The user's ID.

    Returns:
        Optional[dict]: The user's profile data, or None if not found.
    """
    query = "SELECT * FROM user_profiles WHERE user_id = $1;"
    log_database_interaction(query, [user_id])
    return await connection.fetchrow(query, user_id)

async def update_user_profile(connection, user_id: int, updates: dict) -> str:
    """
    Updates a user's profile in the database.

    Args:
        connection: Database connection.
        user_id (int): The user's ID.
        updates (dict): A dictionary of updates to apply.

    Returns:
        str: Result of the update operation.
    """
    set_clause = ", ".join(f"{key} = ${i+1}" for i, key in enumerate(updates.keys()))
    query = f"UPDATE user_profiles SET {set_clause} WHERE user_id = ${len(updates) + 1};"
    parameters = list(updates.values()) + [user_id]
    log_database_interaction(query, parameters)
    return await connection.execute(query, *parameters)

async def create_user_profile(connection, user_id: int, username: str, bio: str = "", avatar_url: str = "") -> str:
    """
    Creates a new user profile.

    Args:
        connection: Database connection.
        user_id (int): The user's ID.
        username (str): The user's username.
        bio (str, optional): The user's bio. Defaults to "".
        avatar_url (str, optional): The user's avatar URL. Defaults to "".

    Returns:
        str: Result of the create operation.
    """
    query = """
        INSERT INTO user_profiles (user_id, username, bio, avatar_url, preferences)
        VALUES ($1, $2, $3, $4, '{}');
    """
    parameters = [user_id, username, bio, avatar_url]
    log_database_interaction(query, parameters)
    return await connection.execute(query, *parameters)

async def delete_user_profile(connection, user_id: int) -> str:
    """
    Deletes a user's profile.

    Args:
        connection: Database connection.
        user_id (int): The user's ID.

    Returns:
        str: Result of the delete operation.
    """
    query = "DELETE FROM user_profiles WHERE user_id = $1;"
    log_database_interaction(query, [user_id])
    return await connection.execute(query, user_id)

# --- Preferences Management ---
async def fetch_user_preferences(connection, user_id: int) -> Optional[dict]:
    """
    Fetches a user's preferences from the database.

    Args:
        connection: Database connection.
        user_id (int): The user's ID.

    Returns:
        Optional[dict]: The user's preferences, or None if not found.
    """
    query = "SELECT setting_key, setting_value FROM user_preferences WHERE user_id = $1;"
    log_database_interaction(query, [user_id])
    rows = await connection.fetch(query, user_id)
    return {row["setting_key"]: row["setting_value"] for row in rows} if rows else None

async def update_user_preference(connection, user_id: int, setting_key: str, setting_value: str) -> str:
    """
    Updates a user's preference in the database.

    Args:
        connection: Database connection.
        user_id (int): The user's ID.
        setting_key (str): The key of the setting to update.
        setting_value (str): The new value for the setting.

    Returns:
        str: Result of the update operation.
    """
    query = """
        INSERT INTO user_preferences (user_id, setting_key, setting_value)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id, setting_key) DO UPDATE SET setting_value = $3;
    """
    parameters = [user_id, setting_key, setting_value]
    log_database_interaction(query, parameters)
    return await connection.execute(query, *parameters)

# --- Achievement Management ---
async def fetch_user_achievements(connection, user_id: int) -> List[dict]:
    """
    Fetches all achievements for a user.

    Args:
        connection: Database connection.
        user_id (int): The user's ID.

    Returns:
        List[dict]: List of achievements.
    """
    query = "SELECT * FROM user_achievements WHERE user_id = $1;"
    log_database_interaction(query, [user_id])
    return await connection.fetch(query, user_id)

async def setup(*args, **kwargs):
    pass
