"""
Economy Helper for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Manage in-bot currency, transactions, and economy systems.

Updates:
- Added robust currency management utilities for balance tracking.
- Integrated reward and transaction logging systems.
- Enhanced support for leaderboards and item purchases.
"""

from typing import Optional, Dict
import random
from loguru import logger

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Facilitate virtual economy management including currency, transactions, and rewards."

# --- Currency Management ---
async def get_user_balance(pool, user_id: int) -> int:
    """
    Retrieves the current balance of a user.

    Args:
        pool: Database connection pool.
        user_id (int): The ID of the user.

    Returns:
        int: The user's current balance.
    """
    query = "SELECT balance FROM user_economy WHERE user_id = $1;"
    try:
        async with pool.acquire() as connection:
            result = await connection.fetchval(query, user_id)
            return result or 0
    except Exception as e:
        logger.error(f"Error fetching balance for user {user_id}: {e}")
        return 0

async def update_user_balance(pool, user_id: int, amount: int) -> bool:
    """
    Updates a user's balance by a specific amount.

    Args:
        pool: Database connection pool.
        user_id (int): The ID of the user.
        amount (int): The amount to add or subtract.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    query = """
    INSERT INTO user_economy (user_id, balance) VALUES ($1, $2)
    ON CONFLICT (user_id) DO UPDATE SET balance = user_economy.balance + $2;
    """
    try:
        async with pool.acquire() as connection:
            await connection.execute(query, user_id, amount)
            logger.info(f"Updated balance for user {user_id} by {amount}.")
            return True
    except Exception as e:
        logger.error(f"Error updating balance for user {user_id}: {e}")
        return False

# --- Transaction Management ---
async def record_transaction(pool, user_id: int, amount: int, transaction_type: str, description: str) -> bool:
    """
    Records a transaction in the database.

    Args:
        pool: Database connection pool.
        user_id (int): The ID of the user.
        amount (int): The amount involved in the transaction.
        transaction_type (str): The type of transaction (e.g., "purchase", "reward").
        description (str): A description of the transaction.

    Returns:
        bool: True if the transaction was recorded, False otherwise.
    """
    query = """
    INSERT INTO transaction_logs (user_id, amount, transaction_type, description, timestamp)
    VALUES ($1, $2, $3, $4, NOW());
    """
    try:
        async with pool.acquire() as connection:
            await connection.execute(query, user_id, amount, transaction_type, description)
            logger.info(f"Transaction recorded for user {user_id}: {transaction_type} ({amount}).")
            return True
    except Exception as e:
        logger.error(f"Error recording transaction for user {user_id}: {e}")
        return False

# --- Reward System ---
async def reward_user(pool, user_id: int, min_reward: int, max_reward: int) -> int:
    """
    Rewards a user with a random amount of currency.

    Args:
        pool: Database connection pool.
        user_id (int): The ID of the user.
        min_reward (int): Minimum reward amount.
        max_reward (int): Maximum reward amount.

    Returns:
        int: The amount rewarded.
    """
    reward = random.randint(min_reward, max_reward)
    if await update_user_balance(pool, user_id, reward):
        await record_transaction(pool, user_id, reward, "reward", "Daily reward")
        logger.info(f"User {user_id} rewarded with {reward} currency.")
        return reward
    return 0

# --- Economy Utilities ---
async def leaderboard(pool, top_n: int = 10) -> Dict[int, int]:
    """
    Retrieves the top users with the highest balances.

    Args:
        pool: Database connection pool.
        top_n (int): Number of users to retrieve.

    Returns:
        Dict[int, int]: A dictionary of user IDs and their balances.
    """
    query = "SELECT user_id, balance FROM user_economy ORDER BY balance DESC LIMIT $1;"
    try:
        async with pool.acquire() as connection:
            results = await connection.fetch(query, top_n)
            return {row["user_id"]: row["balance"] for row in results}
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        return {}

# --- Shop Management ---
async def purchase_item(pool, user_id: int, item_cost: int, item_name: str) -> bool:
    """
    Processes an item purchase for a user.

    Args:
        pool: Database connection pool.
        user_id (int): The ID of the user.
        item_cost (int): The cost of the item.
        item_name (str): The name of the item.

    Returns:
        bool: True if the purchase was successful, False otherwise.
    """
    balance = await get_user_balance(pool, user_id)
    if balance >= item_cost:
        if await update_user_balance(pool, user_id, -item_cost):
            await record_transaction(pool, user_id, -item_cost, "purchase", f"Purchased {item_name}")
            logger.info(f"User {user_id} purchased '{item_name}' for {item_cost} currency.")
            return True
        logger.error(f"Failed to deduct item cost for user {user_id}.")
    else:
        logger.warning(f"User {user_id} has insufficient funds for '{item_name}' (Cost: {item_cost}).")
    return False

async def setup(*args, **kwargs):
    pass
