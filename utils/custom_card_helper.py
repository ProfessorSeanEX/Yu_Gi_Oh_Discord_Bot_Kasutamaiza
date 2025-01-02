"""
Custom Card Helper Functions for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Manage the lifecycle of custom cards, from submission to approval, and provide utilities for managing server-specific card databases.

Updates:
- Enhanced submission, review, and search functionality.
- Added advanced utilities for analyzing and purging card data.
"""

import sys
from typing import List, Dict, Optional
import datetime
from uuid import uuid4
from loguru import logger
from utils.db_manager import initialize_db_manager

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Manage the lifecycle of custom cards for server-specific formats."

# --- Constants ---
CARD_STATUSES = ["Pending", "Approved", "Rejected", "Banned"]

# --- Helper Functions ---
async def submit_card(user_id: int, card_data: dict) -> str:
    """
    Handles card submission by players.

    Args:
        user_id (int): The ID of the user submitting the card.
        card_data (dict): Card details (name, stats, effect, etc.).

    Returns:
        str: Confirmation message or error.
    """
    card_data["status"] = "Pending"
    card_data["submitted_by"] = user_id
    card_data["submission_date"] = datetime.datetime.now()
    card_data["card_id"] = str(uuid4())  # Generate a unique ID for the card

    try:
        await db_manager.db_create("custom_cards", card_data)
        logger.info(f"Card '{card_data['name']}' submitted by user {user_id}.")
        return f"Card '{card_data['name']}' has been submitted for review."
    except Exception as e:
        logger.error(f"Failed to submit card: {e}")
        return "An error occurred while submitting your card."

async def review_card(card_id: str, moderator_id: int, action: str, comments: Optional[str] = None) -> str:
    """
    Allows moderators to review and decide on a card submission.

    Args:
        card_id (str): The unique ID of the card.
        moderator_id (int): The ID of the moderator reviewing the card.
        action (str): Action to take ("approve", "reject", "ban").
        comments (Optional[str]): Additional comments from the moderator.

    Returns:
        str: Confirmation message or error.
    """
    if action.lower() not in ["approve", "reject", "ban"]:
        return "Invalid action. Please use 'approve', 'reject', or 'ban'."

    status = action.capitalize()  # Convert action to status
    update_data = {
        "status": status,
        "moderated_by": moderator_id,
        "moderation_date": datetime.datetime.now(),
        "moderator_comments": comments or "No comments provided.",
    }

    try:
        await db_manager.db_update("custom_cards", update_data, {"card_id": card_id})
        logger.info(f"Card {card_id} reviewed by {moderator_id} with action: {status}.")
        return f"Card '{card_id}' has been {status.lower()}."
    except Exception as e:
        logger.error(f"Failed to review card {card_id}: {e}")
        return "An error occurred while reviewing the card."

async def fetch_user_cards(user_id: int) -> List[dict]:
    """
    Retrieves all cards submitted by a specific user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        List[dict]: List of the user's submitted cards.
    """
    try:
        return await db_manager.db_read("custom_cards", {"submitted_by": user_id})
    except Exception as e:
        logger.error(f"Failed to fetch cards for user {user_id}: {e}")
        return []

async def fetch_cards_by_status(status: str) -> List[dict]:
    """
    Retrieves cards based on their status (e.g., "Pending", "Approved").

    Args:
        status (str): The card status to filter by.

    Returns:
        List[dict]: List of cards matching the status.
    """
    if status not in CARD_STATUSES:
        logger.warning(f"Invalid status '{status}' provided.")
        return []

    try:
        return await db_manager.db_read("custom_cards", {"status": status})
    except Exception as e:
        logger.error(f"Failed to fetch cards with status '{status}': {e}")
        return []

async def search_cards_by_name(name: str) -> List[dict]:
    """
    Searches for cards by name using a fuzzy match.

    Args:
        name (str): The card name to search for.

    Returns:
        List[dict]: Matching cards.
    """
    try:
        return await db_manager.fetch_fuzzy_match("custom_cards", "name", name)
    except Exception as e:
        logger.error(f"Failed to search for cards by name '{name}': {e}")
        return []

# --- Advanced Features ---
async def analyze_pending_cards() -> dict:
    """
    Provides a summary of all pending card submissions.

    Returns:
        dict: Analysis report.
    """
    pending_cards = await fetch_cards_by_status("Pending")
    total = len(pending_cards)
    archetypes = {}
    for card in pending_cards:
        archetype = card.get("archetype", "Generic")
        archetypes[archetype] = archetypes.get(archetype, 0) + 1

    logger.info("Pending cards analyzed.")
    return {
        "Total Pending": total,
        "Archetype Breakdown": archetypes,
    }

async def purge_rejected_cards(days_old: int = 30) -> str:
    """
    Deletes rejected cards older than a specified number of days.

    Args:
        days_old (int): Number of days to consider a card stale.

    Returns:
        str: Confirmation message.
    """
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
    query = f"DELETE FROM custom_cards WHERE status = 'Rejected' AND moderation_date < $1;"
    try:
        await db_manager.execute_with_retry(query, [cutoff_date])
        logger.info(f"Rejected cards older than {days_old} days purged.")
        return f"Rejected cards older than {days_old} days have been deleted."
    except Exception as e:
        logger.error(f"Failed to purge rejected cards: {e}")
        return "An error occurred while purging rejected cards."

async def setup(*args, **kwargs):
    db_manager = initialize_db_manager(bot)
    pass
