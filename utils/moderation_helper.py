"""
Moderation Helper Functions for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Provide reusable utilities for handling user moderation, role management, and server compliance.

Updates:
- Enhanced mute, unmute, kick, and ban utilities with detailed logging and error handling.
- Added robust role and channel permission management functions.
- Streamlined warning management integrated with the database.
"""

from typing import Optional, List
from loguru import logger
import discord

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Streamline user moderation, role enforcement, and server compliance."

# --- Role Management ---
async def ensure_role_exists(guild: discord.Guild, role_name: str, permissions: Optional[discord.Permissions] = None) -> discord.Role:
    """
    Ensures a role exists in the server.

    Args:
        guild (discord.Guild): The server to check.
        role_name (str): The name of the role to ensure.
        permissions (Optional[discord.Permissions]): Permissions to assign to the role.

    Returns:
        discord.Role: The existing or newly created role.
    """
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        logger.info(f"Role '{role_name}' not found. Creating role.")
        role = await guild.create_role(name=role_name, permissions=permissions)
        logger.info(f"Role '{role_name}' created successfully.")
    else:
        logger.debug(f"Role '{role_name}' already exists.")
    return role

async def set_channel_permissions(guild: discord.Guild, role: discord.Role, permissions: discord.PermissionOverwrite):
    """
    Sets permissions for a role across all channels in the guild.

    Args:
        guild (discord.Guild): The server containing the channels.
        role (discord.Role): The role to update permissions for.
        permissions (discord.PermissionOverwrite): Permissions to apply.

    Returns:
        None
    """
    for channel in guild.channels:
        await channel.set_permissions(role, overwrite=permissions)
        logger.info(f"Permissions updated for role '{role.name}' in channel '{channel.name}'.")

# --- Mute Management ---
async def mute_user(guild: discord.Guild, member: discord.Member, reason: str = "No reason provided.") -> Optional[str]:
    """
    Mutes a user by assigning the 'Muted' role.

    Args:
        guild (discord.Guild): The server where the user is muted.
        member (discord.Member): The user to mute.
        reason (str): Reason for the mute.

    Returns:
        Optional[str]: Success message or None if an error occurs.
    """
    try:
        muted_role = await ensure_role_exists(guild, "Muted")
        await member.add_roles(muted_role, reason=reason)
        logger.info(f"User '{member}' has been muted. Reason: {reason}")
        return f"User {member.mention} has been muted."
    except discord.Forbidden:
        logger.error(f"Insufficient permissions to mute '{member}'.")
        return None
    except Exception as e:
        logger.error(f"Error muting user '{member}': {e}")
        return None

async def unmute_user(guild: discord.Guild, member: discord.Member, reason: str = "No reason provided.") -> Optional[str]:
    """
    Unmutes a user by removing the 'Muted' role.

    Args:
        guild (discord.Guild): The server where the user is unmuted.
        member (discord.Member): The user to unmute.
        reason (str): Reason for the unmute.

    Returns:
        Optional[str]: Success message or None if an error occurs.
    """
    try:
        muted_role = discord.utils.get(guild.roles, name="Muted")
        if muted_role and muted_role in member.roles:
            await member.remove_roles(muted_role, reason=reason)
            logger.info(f"User '{member}' has been unmuted. Reason: {reason}")
            return f"User {member.mention} has been unmuted."
        else:
            logger.warning(f"User '{member}' is not muted.")
            return None
    except discord.Forbidden:
        logger.error(f"Insufficient permissions to unmute '{member}'.")
        return None
    except Exception as e:
        logger.error(f"Error unmuting user '{member}': {e}")
        return None

# --- Warning Management ---
async def warn_user(db_manager, user_id: int, issued_by: int, reason: str) -> Optional[str]:
    """
    Issues a warning to a user and logs it in the database.

    Args:
        db_manager: Database manager instance.
        user_id (int): ID of the warned user.
        issued_by (int): ID of the user issuing the warning.
        reason (str): Reason for the warning.

    Returns:
        Optional[str]: Success message or None if an error occurs.
    """
    try:
        data = {"user_id": user_id, "issued_by": issued_by, "reason": reason}
        await db_manager.create("user_warnings", data)
        logger.info(f"User ID '{user_id}' warned by '{issued_by}' for reason: {reason}")
        return f"User <@{user_id}> has been warned."
    except Exception as e:
        logger.error(f"Error warning user '{user_id}': {e}")
        return None

# --- Kick and Ban Utilities ---
async def kick_user(guild: discord.Guild, member: discord.Member, reason: str = "No reason provided.") -> Optional[str]:
    """
    Kicks a user from the server.

    Args:
        guild (discord.Guild): The server where the user is kicked.
        member (discord.Member): The user to kick.
        reason (str): Reason for the kick.

    Returns:
        Optional[str]: Success message or None if an error occurs.
    """
    try:
        await member.kick(reason=reason)
        logger.info(f"User '{member}' has been kicked. Reason: {reason}")
        return f"User {member.mention} has been kicked."
    except discord.Forbidden:
        logger.error(f"Insufficient permissions to kick '{member}'.")
        return None
    except Exception as e:
        logger.error(f"Error kicking user '{member}': {e}")
        return None

async def ban_user(guild: discord.Guild, member: discord.Member, reason: str = "No reason provided.") -> Optional[str]:
    """
    Bans a user from the server.

    Args:
        guild (discord.Guild): The server where the user is banned.
        member (discord.Member): The user to ban.
        reason (str): Reason for the ban.

    Returns:
        Optional[str]: Success message or None if an error occurs.
    """
    try:
        await member.ban(reason=reason)
        logger.info(f"User '{member}' has been banned. Reason: {reason}")
        return f"User {member.mention} has been banned."
    except discord.Forbidden:
        logger.error(f"Insufficient permissions to ban '{member}'.")
        return None
    except Exception as e:
        logger.error(f"Error banning user '{member}': {e}")
        return None

async def setup(*args, **kwargs):
    pass
