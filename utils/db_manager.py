"""
Database utilities for Kasutamaiza Bot.
- Handles database connection pool and interactions.
"""

import asyncpg
import os
from dotenv import load_dotenv
from loguru import logger

# Metadata
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Provide reusable database connection functions for the bot."

# Load environment variables
load_dotenv()


class DatabaseManager:
    """
    Manages the database connection pool and executes queries.
    """

    def __init__(self):
        """
        Initializes the DatabaseManager instance without an active connection pool.
        """
        self.pool = None

    async def initialize_pool(self):
        """
        Initialize the connection pool using environment variables.
        """
        try:
            self.pool = await asyncpg.create_pool(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                min_size=1,
                max_size=10,
                timeout=60.0,  # Optional: Set timeout for acquiring connections
            )
            logger.info("Database connection pool initialized successfully.")
        except Exception as e:
            logger.critical(f"Failed to initialize database pool: {e}")
            raise

    async def fetch(self, query: str, *args):
        """
        Execute a SELECT query and return the results.

        Args:
            query (str): The SQL query to execute.
            *args: Query parameters.

        Returns:
            list[asyncpg.Record]: The query results.
        """
        try:
            async with self.pool.acquire() as connection:
                result = await connection.fetch(query, *args)
                logger.debug(f"Query executed successfully: {query} | Args: {args}")
                return result
        except Exception as e:
            logger.error(f"Failed to execute fetch query: {query} | Args: {args} | Error: {e}")
            raise

    async def execute(self, query: str, *args):
        """
        Execute an INSERT, UPDATE, or DELETE query.

        Args:
            query (str): The SQL query to execute.
            *args: Query parameters.

        Returns:
            str: The status of the executed query.
        """
        try:
            async with self.pool.acquire() as connection:
                result = await connection.execute(query, *args)
                logger.debug(f"Query executed successfully: {query} | Args: {args}")
                return result
        except Exception as e:
            logger.error(f"Failed to execute query: {query} | Args: {args} | Error: {e}")
            raise

    async def close_pool(self):
        """
        Close the database connection pool.
        """
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed successfully.")


# Global instance of the DatabaseManager
db_manager = DatabaseManager()