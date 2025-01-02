"""
Role Management Helper for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Simplify role creation, assignment, and permission adjustments in Discord servers.

Updates:
- Consolidated overlapping functions from `Permission Helper`.
- Enhanced error handling and logging for all role-related operations.
- Streamlined methods for role creation, assignment, and management.
"""

from typing import Optional
import discord
from loguru import logger

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Streamline role management for server administration and user interactions."

# --- Role Management Functions ---
async def create_role(
    guild: discord.Guild,
    role_name: str,
    permissions: discord.Permissions = discord.Permissions.none(),
    color: discord.Color = discord.Color.default()
) -> Optional[discord.Role]:
    """Creates a new role in the guild."""
    try:
        role = await guild.create_role(name=role_name, permissions=permissions, color=color)
        logger.info(f"Role '{role_name}' created in guild '{guild.name}'.")
        return role
    except discord.Forbidden:
        logger.error(f"Insufficient permissions to create role '{role_name}' in guild '{guild.name}'.")
    except Exception as e:
        logger.error(f"Error creating role '{role_name}': {e}")
    return None

async def assign_role(member: discord.Member, role: discord.Role):
    """Assigns a role to a member."""
    if role not in member.roles:
        logger.info(f"Assigning role '{role.name}' to {member.name}.")
        await member.add_roles(role)
    else:
        logger.debug(f"Role '{role.name}' is already assigned to {member.name}.")

async def remove_role(member: discord.Member, role: discord.Role):
    """Removes a role from a member."""
    if role in member.roles:
        logger.info(f"Removing role '{role.name}' from {member.name}.")
        await member.remove_roles(role)
    else:
        logger.debug(f"Role '{role.name}' is not assigned to {member.name}.")

async def delete_role(guild: discord.Guild, role: discord.Role):
    """Deletes a role from the guild."""
    try:
        await role.delete()
        logger.info(f"Role '{role.name}' deleted from guild '{guild.name}'.")
    except discord.Forbidden:
        logger.error(f"Insufficient permissions to delete role '{role.name}' in guild '{guild.name}'.")
    except Exception as e:
        logger.error(f"Error deleting role '{role.name}': {e}")

# --- Role Utilities ---
def get_role_by_name(guild: discord.Guild, role_name: str) -> Optional[discord.Role]:
    """Retrieves a role by name."""
    role = discord.utils.get(guild.roles, name=role_name)
    if role:
        logger.info(f"Role '{role_name}' found in guild '{guild.name}'.")
    else:
        logger.warning(f"Role '{role_name}' not found in guild '{guild.name}'.")
    return role

# --- Permission Management ---
async def update_role_permissions(role: discord.Role, permissions: discord.Permissions):
    """Updates the permissions of a role."""
    try:
        await role.edit(permissions=permissions)
        logger.info(f"Permissions updated for role '{role.name}'.")
    except discord.Forbidden:
        logger.error(f"Insufficient permissions to update role '{role.name}'.")
    except Exception as e:
        logger.error(f"Error updating permissions for role '{role.name}': {e}")

async def adjust_role_hierarchy(guild: discord.Guild, role: discord.Role, position: int):
    """Adjusts the hierarchy of a role."""
    try:
        await guild.edit_role_positions(positions={role: position})
        logger.info(f"Role '{role.name}' moved to position {position} in the hierarchy.")
    except discord.Forbidden:
        logger.error(f"Insufficient permissions to adjust hierarchy for role '{role.name}'.")
    except Exception as e:
        logger.error(f"Error adjusting hierarchy for role '{role.name}': {e}")

async def setup(*args, **kwargs):
    pass
