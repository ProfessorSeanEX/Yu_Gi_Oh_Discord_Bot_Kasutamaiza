"""
Session Management Helper for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Provide utilities for managing user sessions, including state tracking and timeouts.

Updates:
- Added session expiration and cleanup mechanisms.
- Enhanced logging for debugging and transparency.
- Modular design for scalability and maintainability.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from loguru import logger

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Manage user sessions with state tracking, expiration, and concurrency control."

# --- Session Data Structure ---
active_sessions: Dict[int, dict] = {}

# --- Session Management Functions ---
def start_session(user_id: int, session_data: Optional[dict] = None, duration: Optional[int] = 30) -> dict:
    """
    Starts a session for a user.

    Args:
        user_id (int): The ID of the user starting the session.
        session_data (Optional[dict]): Additional data to store in the session.
        duration (Optional[int]): Session duration in minutes. Defaults to 30 minutes.

    Returns:
        dict: The created session details.
    """
    expiration = datetime.now() + timedelta(minutes=duration)
    session = {
        "user_id": user_id,
        "data": session_data or {},
        "started_at": datetime.now(),
        "expires_at": expiration,
    }
    active_sessions[user_id] = session
    logger.info(f"Session started for user {user_id}. Expires at {expiration}.")
    return session

def end_session(user_id: int) -> bool:
    """
    Ends a session for a user.

    Args:
        user_id (int): The ID of the user ending the session.

    Returns:
        bool: True if the session was successfully ended, False otherwise.
    """
    if user_id in active_sessions:
        del active_sessions[user_id]
        logger.info(f"Session ended for user {user_id}.")
        return True
    else:
        logger.warning(f"No active session found for user {user_id}.")
        return False

def get_session(user_id: int) -> Optional[dict]:
    """
    Retrieves an active session for a user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        Optional[dict]: The session details if found, None otherwise.
    """
    session = active_sessions.get(user_id)
    if session:
        if session["expires_at"] > datetime.now():
            return session
        else:
            logger.info(f"Session for user {user_id} has expired.")
            end_session(user_id)
            return None
    else:
        logger.info(f"No active session found for user {user_id}.")
        return None

def is_session_active(user_id: int) -> bool:
    """
    Checks if a session is active for a user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        bool: True if the session is active, False otherwise.
    """
    session = get_session(user_id)
    return session is not None

def extend_session(user_id: int, duration: int) -> bool:
    """
    Extends an active session's expiration time.

    Args:
        user_id (int): The ID of the user.
        duration (int): Additional time to extend in minutes.

    Returns:
        bool: True if the session was extended, False otherwise.
    """
    session = get_session(user_id)
    if session:
        new_expiration = session["expires_at"] + timedelta(minutes=duration)
        session["expires_at"] = new_expiration
        logger.info(f"Session for user {user_id} extended to {new_expiration}.")
        return True
    else:
        logger.warning(f"Cannot extend session for user {user_id}. No active session found.")
        return False

def cleanup_expired_sessions() -> int:
    """
    Cleans up expired sessions.

    Returns:
        int: Number of sessions cleaned up.
    """
    now = datetime.now()
    expired_sessions = [user_id for user_id, session in active_sessions.items() if session["expires_at"] <= now]
    for user_id in expired_sessions:
        del active_sessions[user_id]
        logger.info(f"Cleaned up expired session for user {user_id}.")
    return len(expired_sessions)

async def setup(*args, **kwargs):
    pass
