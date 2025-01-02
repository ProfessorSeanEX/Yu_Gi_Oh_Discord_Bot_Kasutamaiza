"""
Testing/Mocking Helper for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Facilitate unit testing, integration testing, and mocking for various components.

Updates:
- Added robust mocking classes for Discord interactions, database, and external APIs.
- Enhanced utility functions for simulating failures and latencies.
- Optimized logging for better debugging and test traceability.
"""

from typing import Any, Callable, Dict, Optional
from unittest.mock import AsyncMock, Mock
import random
import asyncio
from loguru import logger

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Enable robust testing and mocking capabilities for Discord bot interactions and dependencies."

# --- Mocking Discord Interactions ---
class MockContext:
    """
    A mock context for simulating Discord commands.
    """

    def __init__(self, user_name: str = "TestUser", guild_name: str = "TestGuild"):
        self.user = Mock(name="MockUser", display_name=user_name)
        self.guild = Mock(name="MockGuild", display_name=guild_name)  # Fixed attribute name
        self.channel = Mock(name="MockChannel")
        self.message = Mock(name="MockMessage")
        self.author = self.user
        self.response = AsyncMock(name="MockResponse")

    async def send(self, content: str):
        """
        Simulates sending a message in the context.

        Args:
            content (str): The content of the message.

        Returns:
            Mock: Simulated message object.
        """
        logger.info(f"MockContext.send: {content}")
        return Mock(name="MockMessageSent")

    async def respond(self, content: str, **kwargs):
        """
        Simulates a command response in the context.

        Args:
            content (str): The response content.

        Returns:
            None
        """
        logger.info(f"MockContext.respond: {content}")
        return AsyncMock(name="MockResponseSent")

# --- Mocking Database Responses ---
class MockDatabase:
    """
    A mock database for simulating CRUD operations.
    """

    def __init__(self):
        self.data = {}

    def insert(self, table: str, row: dict):
        """
        Simulates inserting a row into a table.
        """
        if table not in self.data:
            self.data[table] = []
        self.data[table].append(row)
        logger.info(f"Inserted row into table {table}: {row}")

    def fetch(self, table: str, filters: Optional[Dict[str, Any]] = None):
        """
        Simulates fetching rows from a table with optional filters.
        """
        if table not in self.data:
            return []
        results = self.data[table]
        if filters:
            results = [
                row for row in results if all(row.get(key) == value for key, value in filters.items())
            ]
        logger.info(f"Fetched rows from table {table} with filters {filters}: {results}")
        return results

    def update(self, table: str, filters: dict, updates: dict):
        """
        Simulates updating rows in a table.
        """
        if table not in self.data:
            return
        for row in self.data[table]:
            if all(row.get(key) == value for key, value in filters.items()):
                row.update(updates)
                logger.info(f"Updated row in table {table} with filters {filters} and updates {updates}")

    def delete(self, table: str, filters: dict):
        """
        Simulates deleting rows from a table.
        """
        if table not in self.data:
            return
        self.data[table] = [
            row for row in self.data[table] if not all(row.get(key) == value for key, value in filters.items())
        ]
        logger.info(f"Deleted rows from table {table} with filters {filters}")


# --- Mocking External API Calls ---
class MockAPIClient:
    """
    A mock API client for simulating external API responses.
    """

    def __init__(self):
        self.responses = {}

    def set_response(self, endpoint: str, response: Any):
        """
        Sets a mock response for an API endpoint.
        """
        self.responses[endpoint] = response
        logger.info(f"Set mock response for endpoint {endpoint}: {response}")

    async def fetch(self, endpoint: str):
        """
        Simulates fetching data from an API endpoint.
        """
        logger.info(f"MockAPIClient.fetch called for endpoint {endpoint}")
        return self.responses.get(endpoint, {"error": "Endpoint not found"})


# --- Utility Functions for Testing ---
def simulate_random_failure(success_rate: float = 0.9) -> bool:
    """
    Simulates a random failure for stress-testing systems.
    """
    success = random.random() < success_rate
    if not success:
        logger.warning("Simulated random failure occurred.")
    return success


def simulate_latency(min_latency: float = 0.1, max_latency: float = 1.0):
    """
    Simulates latency for testing async systems.
    """
    latency = random.uniform(min_latency, max_latency)
    logger.info(f"Simulating latency of {latency:.2f} seconds.")
    return asyncio.sleep(latency)

async def setup(*args, **kwargs):
    pass
