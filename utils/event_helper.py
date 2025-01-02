"""
Event Helper Functions for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Centralized management of custom events for scalability and flexibility.

Updates:
- Added event registration for both global and guild-specific contexts.
- Integrated event triggering with support for asynchronous callbacks.
- Enhanced utilities for listing registered events and callbacks.
"""

import sys
from typing import Callable, Dict, List, Optional
import asyncio
from loguru import logger

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Manage events flexibly, supporting both global and guild-specific contexts."

# Event registry structure
GLOBAL_EVENTS: Dict[str, List[Callable]] = {}
GUILD_EVENTS: Dict[int, Dict[str, List[Callable]]] = {}

# --- Event Registration ---
def register_global_event(event_name: str, callback: Callable):
    """
    Registers a callback for a global event.

    Args:
        event_name (str): The name of the event.
        callback (Callable): The callback function to execute when the event is triggered.

    Returns:
        None
    """
    if event_name not in GLOBAL_EVENTS:
        GLOBAL_EVENTS[event_name] = []
    GLOBAL_EVENTS[event_name].append(callback)
    logger.info(f"Registered global event '{event_name}' with callback '{callback.__name__}'.")


def register_guild_event(guild_id: int, event_name: str, callback: Callable):
    """
    Registers a callback for a guild-specific event.

    Args:
        guild_id (int): The guild ID for the event.
        event_name (str): The name of the event.
        callback (Callable): The callback function to execute when the event is triggered.

    Returns:
        None
    """
    if guild_id not in GUILD_EVENTS:
        GUILD_EVENTS[guild_id] = {}
    if event_name not in GUILD_EVENTS[guild_id]:
        GUILD_EVENTS[guild_id][event_name] = []
    GUILD_EVENTS[guild_id][event_name].append(callback)
    logger.info(f"Registered event '{event_name}' for guild {guild_id} with callback '{callback.__name__}'.")

# --- Event Deregistration ---
def deregister_global_event(event_name: str, callback: Callable):
    """
    Deregisters a callback from a global event.

    Args:
        event_name (str): The name of the event.
        callback (Callable): The callback function to remove.

    Returns:
        None
    """
    if event_name in GLOBAL_EVENTS and callback in GLOBAL_EVENTS[event_name]:
        GLOBAL_EVENTS[event_name].remove(callback)
        logger.info(f"Deregistered global event '{event_name}' for callback '{callback.__name__}'.")


def deregister_guild_event(guild_id: int, event_name: str, callback: Callable):
    """
    Deregisters a callback from a guild-specific event.

    Args:
        guild_id (int): The guild ID for the event.
        event_name (str): The name of the event.
        callback (Callable): The callback function to remove.

    Returns:
        None
    """
    if guild_id in GUILD_EVENTS and event_name in GUILD_EVENTS[guild_id]:
        if callback in GUILD_EVENTS[guild_id][event_name]:
            GUILD_EVENTS[guild_id][event_name].remove(callback)
            logger.info(f"Deregistered event '{event_name}' for guild {guild_id} and callback '{callback.__name__}'.")

# --- Event Triggering ---
async def trigger_global_event(event_name: str, *args, **kwargs):
    """
    Triggers a global event and executes all associated callbacks.

    Args:
        event_name (str): The name of the event.
        *args: Positional arguments for the callbacks.
        **kwargs: Keyword arguments for the callbacks.

    Returns:
        None
    """
    if event_name in GLOBAL_EVENTS:
        logger.info(f"Triggering global event '{event_name}' with {len(GLOBAL_EVENTS[event_name])} callbacks.")
        await asyncio.gather(*(callback(*args, **kwargs) for callback in GLOBAL_EVENTS[event_name]))


async def trigger_guild_event(guild_id: int, event_name: str, *args, **kwargs):
    """
    Triggers a guild-specific event and executes all associated callbacks.

    Args:
        guild_id (int): The guild ID for the event.
        event_name (str): The name of the event.
        *args: Positional arguments for the callbacks.
        **kwargs: Keyword arguments for the callbacks.

    Returns:
        None
    """
    if guild_id in GUILD_EVENTS and event_name in GUILD_EVENTS[guild_id]:
        callbacks = GUILD_EVENTS[guild_id][event_name]
        logger.info(f"Triggering event '{event_name}' for guild {guild_id} with {len(callbacks)} callbacks.")
        await asyncio.gather(*(callback(*args, **kwargs) for callback in callbacks))

# --- Utility Functions ---
def list_global_events() -> Dict[str, List[str]]:
    """
    Lists all registered global events and their callbacks.

    Returns:
        Dict[str, List[str]]: Event names and callback names.
    """
    events = {event: [callback.__name__ for callback in callbacks] for event, callbacks in GLOBAL_EVENTS.items()}
    logger.debug(f"Global events listed: {events}")
    return events


def list_guild_events(guild_id: int) -> Dict[str, List[str]]:
    """
    Lists all registered events for a specific guild and their callbacks.

    Args:
        guild_id (int): The guild ID.

    Returns:
        Dict[str, List[str]]: Event names and callback names for the guild.
    """
    if guild_id in GUILD_EVENTS:
        events = {
            event: [callback.__name__ for callback in callbacks]
            for event, callbacks in GUILD_EVENTS[guild_id].items()
        }
        logger.debug(f"Guild {guild_id} events listed: {events}")
        return events
    return {}

async def setup(*args, **kwargs):
    pass
