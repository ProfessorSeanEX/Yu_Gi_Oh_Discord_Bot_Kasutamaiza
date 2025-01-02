"""
Rule Enforcement Helper for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Centralized enforcement of server rules with automation and penalty management.

Updates:
- Improved rule loading, checking, and violation handling.
- Added robust penalty enforcement logic, including warnings, mutes, and bans.
- Enhanced logging for rule violations and penalty escalation.
"""

from typing import Dict, List
from datetime import datetime, timedelta
from loguru import logger
import discord
import asyncio

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Automate server rule enforcement and manage penalties consistently."

# --- Rule Management ---
def load_rules_from_file(file_path: str) -> Dict[str, str]:
    """
    Loads rules from a configuration file.

    Args:
        file_path (str): Path to the rules configuration file.

    Returns:
        Dict[str, str]: A dictionary mapping rule IDs to their descriptions.
    """
    try:
        with open(file_path, "r") as file:
            rules = {}
            for line in file:
                if line.strip() and ":" in line:
                    rule_id, description = line.split(":", 1)
                    rules[rule_id.strip()] = description.strip()
            logger.info(f"Loaded {len(rules)} rules from {file_path}")
            return rules
    except FileNotFoundError as e:
        logger.error(f"Rules file not found: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading rules: {e}")
        return {}

def check_rule_violation(message: str, rules: Dict[str, str]) -> List[str]:
    """
    Checks a message against the server rules.

    Args:
        message (str): The message to check.
        rules (Dict[str, str]): Dictionary of rule IDs and descriptions.

    Returns:
        List[str]: List of rule IDs violated by the message.
    """
    violated_rules = []
    for rule_id, rule_description in rules.items():
        if rule_description.lower() in message.lower():
            violated_rules.append(rule_id)
            logger.warning(f"Rule violation detected: {rule_id}")
    return violated_rules

# --- Penalty Management ---
def assign_penalty(violations: List[str], escalation_policy: Dict[int, str]) -> str:
    """
    Assigns a penalty based on the number of violations.

    Args:
        violations (List[str]): List of violated rule IDs.
        escalation_policy (Dict[int, str]): Mapping of violation counts to penalties.

    Returns:
        str: The assigned penalty.
    """
    violation_count = len(violations)
    penalty = escalation_policy.get(violation_count, "No penalty assigned.")
    logger.info(f"Assigned penalty: {penalty}")
    return penalty

async def enforce_penalty(bot, guild, member, penalty: str):
    """
    Enforces the assigned penalty on a user.

    Args:
        bot: The bot instance.
        guild: The guild (server) instance.
        member: The member to penalize.
        penalty (str): The penalty to enforce.

    Returns:
        None
    """
    if penalty.startswith("Warning"):
        await member.send(f"You have been warned: {penalty}")
    elif penalty.startswith("Mute"):
        duration = int(penalty.split()[1])  # Extract duration in minutes
        muted_role = discord.utils.get(guild.roles, name="Muted")
        if not muted_role:
            muted_role = await guild.create_role(name="Muted")
            for channel in guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)
        await member.add_roles(muted_role, reason="Rule violation")
        logger.info(f"{member} muted for {duration} minutes.")
        await asyncio.sleep(duration * 60)
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            logger.info(f"{member} has been unmuted after serving {duration} minutes.")
    elif penalty.startswith("Ban"):
        await guild.ban(member, reason="Rule violation")
        logger.info(f"{member} has been banned for rule violations.")

# --- Escalation Policies ---
def default_escalation_policy() -> Dict[int, str]:
    """
    Returns a default escalation policy.

    Returns:
        Dict[int, str]: A mapping of violation counts to penalties.
    """
    return {
        1: "Warning issued.",
        2: "Mute for 15 minutes.",
        3: "Ban from the server.",
    }

# --- Rule Violation Logging ---
def log_rule_violation(member_id: int, violated_rules: List[str], log_file: str = "violations.log"):
    """
    Logs a member's rule violations.

    Args:
        member_id (int): The ID of the violating member.
        violated_rules (List[str]): List of rule IDs violated.
        log_file (str): Path to the log file.

    Returns:
        None
    """
    try:
        with open(log_file, "a") as file:
            timestamp = datetime.now().isoformat()
            log_entry = f"{timestamp} - User {member_id} violated rules: {', '.join(violated_rules)}\n"
            file.write(log_entry)
        logger.info(f"Logged rule violations for user {member_id}.")
    except Exception as e:
        logger.error(f"Failed to log rule violation: {e}")

async def setup(*args, **kwargs):
    pass
