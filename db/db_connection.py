import os
import asyncpg
import ssl
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into the environment

# Retrieve environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Validate environment variables
missing_vars = []
for var_name, var_value in [("DB_HOST", DB_HOST), ("DB_PORT", DB_PORT),
                            ("DB_USER", DB_USER), ("DB_PASSWORD", DB_PASSWORD),
                            ("DB_NAME", DB_NAME)]:
    if not var_value:
        missing_vars.append(var_name)

if missing_vars:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

# Convert DB_PORT to integer
try:
    DB_PORT = int(DB_PORT)
except ValueError:
    raise ValueError("DB_PORT must be an integer.")

# Optional: Configure SSL if required
USE_SSL = os.getenv("USE_SSL", "False").lower() in ("true", "1", "yes")

if USE_SSL:
    # Create an SSL context (customize as needed)
    ssl_context = ssl.create_default_context()
    # If you need to disable hostname checking or certificate verification (not recommended):
    # ssl_context.check_hostname = False
    # ssl_context.verify_mode = ssl.CERT_NONE
else:
    ssl_context = None  # SSL is not used

async def create_db_pool():
    """Create and return a global connection pool for PostgreSQL."""
    try:
        return await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            ssl=ssl_context
        )
    except Exception as e:
        # Log the exception or handle it as needed
        print(f"Failed to create database pool: {e}")
        raise
