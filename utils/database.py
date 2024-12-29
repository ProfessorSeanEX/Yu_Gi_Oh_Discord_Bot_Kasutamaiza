"""
Database utilities for Kasutamaiza Bot.
- Handles database connections and interactions.
"""

import asyncpg
import os

# Metadata
__purpose__ = "Provide reusable database connection functions."

async def connect():
    """
    Connect to the PostgreSQL database using asyncpg.
    Returns:
        asyncpg.Connection: An active database connection.
    """
    return await asyncpg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )