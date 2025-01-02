# --- Metadata ---
"""
Database Manager for Kasutamaiza Bot.
Manages connection pooling, schema validation, and advanced database operations.

Metadata:
- Version: 1.0.3
- Author: ProfessorSeanEX
- Purpose: Orchestrate database interactions by integrating modular helpers.
"""


# --- Imports ---

# Standard Library Imports
import os  # For environment variable management.
import sys  # For runtime interaction and debugging.
from pathlib import Path  # For handling file paths consistently.

# Third-Party Library Imports
import discord  # For Discord API integration and bot context.
import asyncpg  # For asynchronous PostgreSQL database operations.

# --- Utility Modules: Database Helpers ---
from utils import inject_helpers_into_namespace
inject_helpers_into_namespace(globals())  # Dynamically load all known helpers.

# Metadata [for the file]
__version__ = "1.0.3"
__author__ = "ProfessorSeanEX"
__purpose__ = "Orchestrate database interactions by integrating modular helpers."


# --- Constants and Configuration ---
# Load environment variables from a .env file for local development and deployment flexibility.


# Table schemas define the structure of the database tables used by the bot.
# These schemas ensure that tables are created if they do not already exist.
TABLE_SCHEMAS = {
    # Table for storing bot users with essential information.
    "bot_users": """
        CREATE TABLE IF NOT EXISTS bot_users (
            user_id BIGINT PRIMARY KEY,                -- Unique user identifier
            username TEXT NOT NULL,                   -- Username of the bot user
            join_date TIMESTAMPTZ DEFAULT NOW(),      -- Timestamp when the user joined
            elo_rating INTEGER DEFAULT 1200,         -- Default ELO rating for ranking
            is_admin BOOLEAN DEFAULT FALSE           -- Flag for admin users
        );
    """,
    
    # Table for logging user achievements.
    "user_achievements": """
        CREATE TABLE IF NOT EXISTS user_achievements (
            achievement_id SERIAL PRIMARY KEY,       -- Unique identifier for each achievement
            user_id BIGINT NOT NULL,                 -- User ID associated with the achievement
            achievement_name TEXT NOT NULL,          -- Name of the achievement
            date_earned TIMESTAMPTZ DEFAULT NOW(),   -- Timestamp of when the achievement was earned
            CONSTRAINT fk_user_achievements_user FOREIGN KEY (user_id)
                REFERENCES bot_users (user_id)       -- Foreign key constraint linking to bot_users
                ON UPDATE NO ACTION
                ON DELETE CASCADE
        );
    """,
    
    # Table for storing activity logs for users.
    "user_activity_logs": """
        CREATE TABLE IF NOT EXISTS user_activity_logs (
            log_id SERIAL PRIMARY KEY,              -- Unique log identifier
            user_id BIGINT NOT NULL,                -- User ID associated with the activity
            timestamp TIMESTAMPTZ DEFAULT NOW(),    -- Timestamp of the logged activity
            action_type TEXT NOT NULL,              -- Type of action performed
            details JSON,                           -- JSON field for additional details
            CONSTRAINT fk_user_activity_user FOREIGN KEY (user_id)
                REFERENCES bot_users (user_id)      -- Foreign key linking to bot_users
                ON UPDATE NO ACTION
                ON DELETE CASCADE
        );
    """,
    
    # Table for storing user preferences.
    "user_preferences": """
        CREATE TABLE IF NOT EXISTS user_preferences (
            preference_id SERIAL PRIMARY KEY,       -- Unique preference identifier
            user_id BIGINT NOT NULL,                -- User ID associated with the preference
            setting_key TEXT NOT NULL,              -- Key representing the setting name
            setting_value TEXT NOT NULL,            -- Value of the setting
            CONSTRAINT fk_user_preferences_user FOREIGN KEY (user_id)
                REFERENCES bot_users (user_id)      -- Foreign key linking to bot_users
                ON UPDATE NO ACTION
                ON DELETE CASCADE
        );
    """,
    
    # Table for managing user profiles with extended information.
    "user_profiles": """
        CREATE TABLE IF NOT EXISTS user_profiles (
            profile_id SERIAL PRIMARY KEY,          -- Unique profile identifier
            user_id BIGINT NOT NULL,                -- User ID linked to the profile
            bio TEXT,                               -- Bio or description of the user
            avatar_url TEXT,                        -- URL of the user's avatar
            preferences JSON,                       -- JSON for additional preferences
            CONSTRAINT fk_user_id FOREIGN KEY (user_id)
                REFERENCES bot_users (user_id)      -- Foreign key linking to bot_users
                ON UPDATE NO ACTION
                ON DELETE CASCADE
        );
    """,
    
    # Table for issuing and tracking warnings for users.
    "user_warnings": """
        CREATE TABLE IF NOT EXISTS user_warnings (
            warning_id SERIAL PRIMARY KEY,          -- Unique identifier for each warning
            user_id BIGINT NOT NULL,                -- User ID associated with the warning
            issued_by BIGINT NOT NULL,              -- ID of the admin issuing the warning
            reason TEXT NOT NULL,                   -- Reason for the warning
            timestamp TIMESTAMPTZ DEFAULT NOW(),    -- Timestamp when the warning was issued
            CONSTRAINT fk_user_warnings_issued_by FOREIGN KEY (issued_by)
                REFERENCES bot_users (user_id)      -- Foreign key linking to the admin in bot_users
                ON UPDATE NO ACTION
                ON DELETE SET NULL,
            CONSTRAINT fk_user_warnings_user FOREIGN KEY (user_id)
                REFERENCES bot_users (user_id)      -- Foreign key linking to bot_users
                ON UPDATE NO ACTION
                ON DELETE CASCADE
        );
    """,
    # Insert new tables here
}


# --- Initialization and Setup ---
"""
DatabaseManager Class Initialization and Setup

Purpose:
- Initializes the DatabaseManager class for managing database operations.
- Establishes a connection pool, validates table schemas, and provides utility methods.

Notes:
- Requires `discord.Bot` instance and environment variables for configuration.
"""

class DatabaseManager:
    """
    Handles the database operations, including connection pooling, schema management,
    and providing utility methods for interaction with the database.

    Attributes:
        bot (discord.Bot): Reference to the bot instance for accessing context.
        pool (asyncpg.Pool): Connection pool for managing database connections efficiently.
    """

    def __init__(self, bot: discord.Bot, env_vars: dict):
        """
        Initializes the DatabaseManager instance.

        Args:
            bot (discord.Bot): The bot instance for context.
            env_vars (dict): Validated environment variables for database configuration.

        Notes:
            - The `env_vars` parameter provides all required database connection settings.
        """
        self.bot = bot  # Reference to the bot instance.
        self.env_vars = env_vars  # Store environment variables for later use.
        self.pool = None  # Connection pool to be initialized later.

        log_custom("INFO", "DatabaseManager initialized with provided environment variables.")

    async def initialize_pool(self):
        """
        Establishes the database connection pool using validated environment variables.

        Workflow:
        1. Validates the required environment variables using `EnvironmentHelper`.
        2. Creates an asynchronous connection pool with the validated variables.
        3. Logs the success or failure of the operation.

        Raises:
            RuntimeError: If environment variables are invalid or the pool fails to initialize.
        """
        log_custom("INFO", "Initializing database connection pool...")

        # Check if the pool is already initialized to prevent duplication.
        if getattr(self.bot, "_db_pool_initialized", False):
            log_custom("DEBUG", "Database connection pool already initialized. Skipping initialization.")
            return self.bot.db_pool

        # Step 1: Validate required environment variables for database configuration.
        required_vars = {
            "DB_HOST": str,
            "DB_PORT": int,
            "DB_USER": str,
            "DB_PASSWORD": str,
            "DB_NAME": str,
        }
        env_vars = validate_required_environment_variables(required_vars)
        log_custom("DEBUG", f"Environment variables validated: {list(env_vars.keys())}")

        # Step 2: Create the connection pool using the validated environment variables.
        try:
            self.pool = await asyncpg.create_pool(
                host=env_vars["DB_HOST"],
                port=env_vars["DB_PORT"],
                user=env_vars["DB_USER"],
                password=env_vars["DB_PASSWORD"],
                database=env_vars["DB_NAME"],
            )
            self.bot._db_pool_initialized = True  # Mark the pool as initialized for lifecycle tracking.
            log_custom("INFO", "Database connection pool initialized successfully.")
        except Exception as e:
            log_error("Database Connection Pool Initialization", e)
            raise RuntimeError("Database connection pool initialization failed.") from e

        return self.pool

    async def ensure_table_schemas(self):
        """
        Ensures that all required tables exist in the database by validating and creating schemas.

        Workflow:
        1. Acquires a connection from the pool.
        2. Iterates through `TABLE_SCHEMAS` to validate and create each table.
        3. Logs the success or failure for each table operation.

        Raises:
            Exception: If any table schema validation or creation fails.
        """
        log_custom("INFO", "Validating and ensuring table schemas...")
        async with self.pool.acquire() as connection:
            for table_name, schema in TABLE_SCHEMAS.items():
                try:
                    # Execute schema creation SQL to validate or create the table.
                    await connection.execute(schema)
                    log_custom("INFO", f"Table '{table_name}' schema validated or created successfully.")
                except Exception as e:
                    log_error(f"Schema Validation or Creation: {table_name}", e)
                    raise



    # --- Core Database Operations ---
    """
    Core Database Operations

    Purpose:
    - Provides utility methods for interacting with the database.
    - Includes support for bulk inserts, updates, paginated queries, and fuzzy search.

    Notes:
    - Each method logs key actions, parameters, and outcomes using LoggingHelper.
    """

    async def insert_bulk(self, table: str, rows: list[dict]):
        """
        Inserts multiple rows into a specified table.

        Args:
            table (str): Name of the table where rows should be inserted.
            rows (list[dict]): A list of dictionaries representing rows to insert.

        Workflow:
            1. Acquires a database connection from the pool.
            2. Constructs and executes an `INSERT` statement for each row.
            3. Logs the success or failure of the operation.

        Raises:
            Exception: If the insertion fails for any reason.
        """
        log_custom("INFO", f"Inserting bulk data into table '{table}'...")
        try:
            async with self.pool.acquire() as connection:
                for row in rows:
                    # Generate query dynamically based on row data.
                    columns = ", ".join(row.keys())
                    placeholders = ", ".join(f"${i}" for i in range(1, len(row) + 1))
                    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                    await connection.execute(query, *row.values())
                log_custom("INFO", f"Bulk data inserted into table '{table}' successfully.")
        except Exception as e:
            log_error(f"Bulk Insert into {table}", e)
            raise

    async def update_bulk(self, table: str, updates: list[dict], key_column: str):
        """
        Updates multiple rows in a table in bulk based on a key column.

        Args:
            table (str): Name of the table to update.
            updates (list[dict]): A list of dictionaries, where each dictionary represents
                                a row to update. Keys are column names, and values are the
                                new values for those columns.
            key_column (str): Column name used to identify rows for update.

        Workflow:
        1. Iterates through the `updates` list and constructs an `UPDATE` query dynamically.
        2. Executes the query for each row, using the `key_column` to target the row.
        3. Logs the query and parameters for traceability.

        Raises:
            Exception: If any update operation fails.
        """
        log_custom("INFO", f"Updating rows in table '{table}' in bulk...")
        try:
            async with self.pool.acquire() as connection:
                for update in updates:
                    # Construct the SET clause dynamically based on the update dictionary.
                    set_clause = ", ".join(f"{column} = ${idx}" for idx, column in enumerate(update.keys(), start=1))
                    query = f"UPDATE {table} SET {set_clause} WHERE {key_column} = ${len(update) + 1}"
                    params = list(update.values()) + [update[key_column]]
                    log_database_interaction(query, params)
                    await connection.execute(query, *params)
                log_custom("INFO", f"Bulk updates completed for table '{table}'.")
        except Exception as e:
            log_error(f"Bulk Update in {table}", e)
            raise

    async def fetch_paginated_rows(self, table: str, filters: dict, page: int, page_size: int):
        """
        Fetches rows from a table with pagination and optional filters.

        Args:
            table (str): Name of the table to query.
            filters (dict): Key-value pairs for column-based filtering.
            page (int): Page number to fetch (starting at 1).
            page_size (int): Number of rows per page.

        Returns:
            list[dict]: List of rows matching the filters, paginated.

        Workflow:
            1. Builds a dynamic SQL query, incorporating filters if provided.
            2. Calculates the offset based on the page number and page size.
            3. Executes the query and retrieves the paginated results.
            4. Logs the query, parameters, and results for traceability.
        """
        log_custom("INFO", f"Fetching paginated rows from table '{table}', page {page}, page size {page_size}...")
        try:
            # Calculate the OFFSET for pagination.
            offset = (page - 1) * page_size

            # Start constructing the SQL query dynamically.
            query = f"SELECT * FROM {table}"
            conditions = []
            params = []

            # Add filter conditions to the query if provided.
            if filters:
                for idx, (column, value) in enumerate(filters.items(), start=1):
                    conditions.append(f"{column} = ${idx}")
                    params.append(value)
                query += " WHERE " + " AND ".join(conditions)

            # Append pagination clauses (LIMIT and OFFSET) to the query.
            query += f" LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
            params.extend([page_size, offset])

            log_database_interaction(query, params)
            async with self.pool.acquire() as connection:
                rows = await connection.fetch(query, *params)
                log_custom("INFO", f"Fetched {len(rows)} rows from table '{table}'.")
                return [dict(row) for row in rows]
        except Exception as e:
            log_error(f"Paginated Fetch from {table}", e)
            raise

    async def fetch_fuzzy_match(self, table: str, column: str, search_term: str):
        """
        Performs a fuzzy search on a specific column within a table.

        Args:
            table (str): Name of the table to search.
            column (str): Column name where the search is performed.
            search_term (str): Search term to match, using a case-insensitive and partial match.

        Returns:
            list[dict]: Rows from the table that match the search term.

        Workflow:
            1. Constructs a SQL query using the `ILIKE` operator for case-insensitive pattern matching.
            2. Logs the constructed query and parameters.
            3. Executes the query and retrieves matching rows.
            4. Converts the results into a list of dictionaries for easy processing.
        """
        log_custom("INFO", f"Performing fuzzy search on table '{table}' for column '{column}' with term '{search_term}'...")
        try:
            # Construct the fuzzy search query.
            query = f"SELECT * FROM {table} WHERE {column} ILIKE $1"
            params = [f"%{search_term}%"]
            log_database_interaction(query, params)

            # Execute the query and fetch results.
            async with self.pool.acquire() as connection:
                rows = await connection.fetch(query, *params)
                log_custom("INFO", f"Fuzzy search fetched {len(rows)} rows from table '{table}'.")
                return [dict(row) for row in rows]
        except Exception as e:
            log_error(f"Fuzzy Search in {table}", e)
            raise


    # --- Resilient Query Execution ---
    """
    Resilient Query Execution

    Purpose:
    - Provides utility functions to handle database operations with retry mechanisms.

    Notes:
    - Designed to ensure reliability during transient errors, such as network issues.
    """

    async def execute_query_with_retry(self, query: str, retries: int = 3, *params):
        """
        Executes a SQL query with retry logic for handling transient errors.

        Args:
            query (str): The SQL query string to execute.
            retries (int): Maximum number of retry attempts for transient errors.
            params: Parameters for the SQL query.

        Returns:
            list[asyncpg.Record]: Query results.

        Workflow:
            1. Attempts to execute the query using the connection pool.
            2. If an error occurs, retries the query up to `retries` times.
            3. Logs every attempt, including successes and failures.

        Notes:
            - Retries are designed for transient issues like network instability.
            - Fails gracefully after exhausting all retries.
        """
        log_custom("INFO", f"Executing query with retry logic. Retries allowed: {retries}")
        for attempt in range(1, retries + 1):
            try:
                # Acquire a connection from the pool and execute the query.
                async with self.pool.acquire() as connection:
                    result = await connection.fetch(query, *params)
                    log_custom("INFO", f"Query executed successfully on attempt {attempt}.")
                    return result
            except Exception as e:
                log_custom("WARNING", f"Query failed on attempt {attempt}: {str(e)}")
                if attempt == retries:
                    log_error("Max Retry Attempts Reached", e)
                    raise
                log_custom("DEBUG", "Retrying query...")


    # --- Transaction Management ---
    """
    Transaction Management

    Purpose:
    - Ensures atomicity for multiple dependent database operations.
    - Provides an interface for executing a sequence of operations as a single transaction.

    Notes:
    - Logs each operation within the transaction for traceability.
    """

    async def manage_transaction(self, operations: list[callable]):
        """
        Executes a series of database operations within a single transaction.

        Args:
            operations (list[callable]): A list of async functions, each representing
                                        a database operation to execute within the transaction.

        Workflow:
            1. Acquires a connection from the pool and begins a transaction.
            2. Sequentially executes all provided operations within the transaction context.
            3. Commits the transaction if all operations succeed.
            4. Rolls back the transaction and logs errors if any operation fails.

        Notes:
            - This method ensures data consistency by grouping dependent operations.
            - Transactions are particularly useful for batch inserts, updates, or
            any operation requiring atomicity.

        Raises:
            Exception: If any operation within the transaction fails, the entire
                    transaction is rolled back.
        """
        log_custom("INFO", "Starting database transaction...")
        async with self.pool.acquire() as connection:
            transaction = connection.transaction()
            await transaction.start()
            try:
                # Execute all operations sequentially within the transaction.
                for operation in operations:
                    log_custom("DEBUG", f"Executing transaction operation: {operation.__name__}")
                    await operation(connection)
                await transaction.commit()
                log_custom("INFO", "Transaction committed successfully.")
            except Exception as e:
                # Roll back the transaction if any operation fails.
                await transaction.rollback()
                log_error("Transaction Failed", e)
                raise


    # --- Cleanup and Shutdown ---
    """
    Cleanup and Shutdown

    Purpose:
    - Ensures proper resource deallocation during bot shutdown.
    - Manages the graceful closure of database connections.

    Notes:
    - Logs each step of the cleanup process for traceability.
    """

    async def close_pool(self):
        """
        Closes the database connection pool during the bot's shutdown sequence.

        Workflow:
        1. Checks if the pool is already initialized.
        2. Gracefully closes all active connections in the pool.
        3. Logs the success or failure of the operation.

        Raises:
            RuntimeError: If the pool closure fails.
        """
        if self.pool:
            log_custom("INFO", "Closing database connection pool...")
            try:
                await self.pool.close()
                log_custom("INFO", "Database connection pool closed successfully.")
            except Exception as e:
                log_error("Database Connection Pool Closure", e)
                raise RuntimeError("Database connection pool closure failed.") from e


# --- Setup Integration ---
"""
Setup Integration

Purpose:
- Initializes the `DatabaseManager` during bot startup.
- Validates environment variables, sets up connection pooling, and ensures schema readiness.

Notes:
- Centralized setup for consistent database integration.
- Full integration with `LoggingHelper` for detailed logging and error tracking.
"""

async def setup(bot: discord.Bot, *args, **kwargs):
    """
    Sets up the DatabaseManager during bot startup.

    Workflow:
    1. Validates required environment variables.
    2. Initializes the `DatabaseManager` instance.
    3. Establishes connection pooling.
    4. Validates and creates table schemas.

    Raises:
        Exception: If setup fails at any stage.
    """
    log_custom("INFO", "Starting DatabaseManager setup...")

    try:
        # Step 1: Validate environment variables
        env_vars = validate_required_environment_variables({
            "DB_HOST": str,
            "DB_PORT": int,
            "DB_USER": str,
            "DB_PASSWORD": str,
            "DB_NAME": str,
        })
        log_custom("INFO", f"Environment variables validated: {', '.join(env_vars.keys())}")

        # Step 2: Initialize the DatabaseManager instance
        db_manager = DatabaseManager(bot, env_vars)
        log_custom("INFO", "DatabaseManager instance initialized.")

        # Step 3: Set up the connection pool
        await db_manager.initialize_pool()
        log_custom("INFO", "Database connection pool initialized.")

        # Step 4: Validate and create table schemas
        await db_manager.ensure_table_schemas()
        log_custom("INFO", "Database schemas validated and created successfully.")

        # Attach the DatabaseManager instance to the bot
        bot.db_manager = db_manager
        log_custom("INFO", "DatabaseManager setup completed successfully.")
    except Exception as e:
        log_error("DatabaseManager Setup", e)
        raise
