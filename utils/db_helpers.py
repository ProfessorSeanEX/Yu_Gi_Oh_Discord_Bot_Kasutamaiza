"""
Database Helper Functions for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Advanced utilities for CRUD operations, schema validation, performance logging, and transactional support.

Updates:
- Integrated migrated function `format_filters` from `helper.py`.
- Optimized structure for modularity and performance.
- Enhanced logging for debugging and query tracing.
"""

from typing import Optional, List, Dict
import asyncpg
from loguru import logger

# --- Inline Filters Formatter ---
def format_filters(filters: dict) -> str:
    """
    Formats filters into a SQL-compatible WHERE clause.

    Args:
        filters (dict): Filters to format.

    Returns:
        str: SQL WHERE clause.
    """
    return " AND ".join([f"{key} = ${i+1}" for i, key in enumerate(filters.keys())])

# --- CRUD Operations ---
async def db_create(connection, table: str, data: dict):
    """
    Insert a single row into the specified table.
    """
    keys = ', '.join(data.keys())
    values = ', '.join(f"${i + 1}" for i in range(len(data)))
    query = f"INSERT INTO {table} ({keys}) VALUES ({values})"
    await connection.execute(query, *data.values())
    logger.info(f"Row inserted into table {table}: {data}")


async def db_read(connection, table: str, filters: dict):
    """
    Read rows from the specified table with filters.
    """
    if filters:
        conditions = ' AND '.join(f"{key} = ${i + 1}" for i, key in enumerate(filters))
        query = f"SELECT * FROM {table} WHERE {conditions}"
        rows = await connection.fetch(query, *filters.values())
    else:
        query = f"SELECT * FROM {table}"
        rows = await connection.fetch(query)
    logger.info(f"Rows fetched from table {table}: {len(rows)} rows found.")
    return rows


async def db_update(connection, table: str, updates: dict, filters: dict):
    """
    Update rows in the specified table.
    """
    set_clause = ', '.join(f"{key} = ${i + 1}" for i, key in enumerate(updates))
    filter_clause = ' AND '.join(
        f"{key} = ${i + 1 + len(updates)}" for i, key in enumerate(filters)
    )
    query = f"UPDATE {table} SET {set_clause} WHERE {filter_clause}"
    await connection.execute(query, *updates.values(), *filters.values())
    logger.info(f"Rows updated in table {table}: {updates} with filters {filters}")


async def db_delete(connection, table: str, filters: dict):
    """
    Delete rows from the specified table with filters.
    """
    conditions = ' AND '.join(f"{key} = ${i + 1}" for i, key in enumerate(filters))
    query = f"DELETE FROM {table} WHERE {conditions}"
    await connection.execute(query, *filters.values())
    logger.info(f"Rows deleted from table {table} with filters {filters}")

# --- Bulk Operations ---
async def insert_bulk_rows(connection, table: str, rows: list[dict]):
    """
    Insert multiple rows into the specified table.
    """
    if not rows:
        logger.warning(f"No rows provided for bulk insert into {table}.")
        return
    keys = ', '.join(rows[0].keys())
    values = ', '.join(f"${i + 1}" for i in range(len(rows[0])))
    query = f"INSERT INTO {table} ({keys}) VALUES ({values})"
    await connection.executemany(query, [tuple(row.values()) for row in rows])
    logger.info(f"Bulk insert into table {table}: {len(rows)} rows.")


async def update_bulk_rows(connection, table: str, updates: list[dict], key_column: str):
    """
    Update multiple rows in bulk.
    """
    for row in updates:
        filters = {key_column: row[key_column]}
        await db_update(connection, table, row, filters)
    logger.info(f"Bulk update in table {table}: {len(updates)} rows.")

# --- Advanced Utilities ---
async def fetch_paginated(connection, table: str, filters: dict, page: int, page_size: int):
    """
    Fetch rows with pagination from the specified table.
    """
    offset = (page - 1) * page_size
    filter_clause = ' AND '.join(f"{key} = ${i + 1}" for i, key in enumerate(filters))
    query = f"""
        SELECT * FROM {table}
        WHERE {filter_clause}
        LIMIT {page_size} OFFSET {offset}
    """
    rows = await connection.fetch(query, *filters.values())
    logger.info(f"Paginated fetch from table {table}: {len(rows)} rows on page {page}.")
    return rows

async def fetch_fuzzy_match(connection, table: str, column: str, search_term: str):
    """
    Fetch rows using fuzzy matching from the specified table.
    """
    query = f"SELECT * FROM {table} WHERE {column} ILIKE $1"
    rows = await connection.fetch(query, f"%{search_term}%")
    logger.info(f"Fuzzy match fetch from table {table}: {len(rows)} rows for search '{search_term}'.")
    return rows
    
# --- Schema Management ---
async def validate_and_upgrade_schema(connection, table: str, schema: str) -> None:
    """
    Validates and upgrades a table's schema.
    """
    logger.debug(f"Validating/upgrading schema for {table}")
    try:
        await connection.execute(schema)
        logger.info(f"Schema for {table} validated or upgraded.")
    except asyncpg.PostgresError as e:
        logger.error(f"Failed to validate/upgrade schema for {table}: {e}")
        raise

# --- Transactional Support ---
async def db_transaction(pool, queries: List[dict]) -> bool:
    """
    Executes multiple queries within a transaction.
    """
    async with pool.acquire() as connection:
        async with connection.transaction():
            try:
                for query in queries:
                    logger.debug(f"Executing query: {query['query']} | Parameters: {query.get('params', [])}")
                    await connection.execute(query['query'], *query.get('params', []))
                return True
            except Exception as e:
                logger.error(f"Transaction failed: {e}")
                raise

async def setup(*args, **kwargs):
    pass
