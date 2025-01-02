"""
Transaction Helper for Database Management.
- Handles transactional operations for database queries.

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX
- Purpose: Simplify transactional operations in the database.
"""

from loguru import logger

# Metadata
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Simplify transactional operations in the database."

async def begin_transaction(connection):
    """
    Begins a database transaction.

    Args:
        connection (asyncpg.Connection): The database connection.

    Returns:
        asyncpg.transaction.Transaction: The started transaction.
    """
    transaction = connection.transaction()
    await transaction.start()
    logger.info("Transaction started.")
    return transaction

async def commit_transaction(transaction):
    """
    Commits a database transaction.

    Args:
        transaction (asyncpg.transaction.Transaction): The transaction to commit.

    Returns:
        None
    """
    await transaction.commit()
    logger.info("Transaction committed.")

async def rollback_transaction(transaction):
    """
    Rolls back a database transaction.

    Args:
        transaction (asyncpg.transaction.Transaction): The transaction to roll back.

    Returns:
        None
    """
    await transaction.rollback()
    logger.warning("Transaction rolled back.")

async def setup(*args, **kwargs):
    pass
