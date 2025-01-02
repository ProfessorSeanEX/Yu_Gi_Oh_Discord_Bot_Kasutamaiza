"""
Connection Helper for Database Management.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Simplify database connection management.
"""

import asyncpg
import os
from dotenv import load_dotenv
from loguru import logger

# Metadata
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Simplify database connection management."

# Load environment variables
load_dotenv()

async def initialize_connection_pool():
    """
    Initializes the database connection pool using environment variables.
    """
    try:
        pool = await asyncpg.create_pool(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5432),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            min_size=1,
            max_size=10,
            timeout=60.0,
            ssl=os.getenv("DB_SSL", "require")  # Optional for SSL setup
        )
        logger.info("Database connection pool initialized successfully.")
        return pool
    except asyncpg.PostgresError as e:
        logger.critical(f"Failed to initialize database pool: {e}")
        raise

async def close_connection_pool(pool):
    """
    Closes the database connection pool.
    """
    if pool:
        await pool.close()
        logger.info("Database connection pool closed successfully.")

async def setup(*args, **kwargs):
    pass
