import os
import asyncpg
import ssl
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
USE_SSL = os.getenv("USE_SSL", "False").lower() in ("true", "1", "yes")
DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", 30))  # Default timeout to 30 seconds

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

# Configure SSL if required
ssl_context = None
if USE_SSL:
    ssl_context = ssl.create_default_context()
    # Debugging note: Use these options only if SSL verification fails (not recommended for production)
    if os.getenv("DISABLE_SSL_VERIFICATION", "False").lower() in ("true", "1", "yes"):
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

async def create_db_pool():
    """Create and return a global connection pool for PostgreSQL."""
    try:
        print(f"Attempting connection to {DB_HOST}:{DB_PORT} with SSL={USE_SSL}")
        pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            ssl=ssl_context,
            timeout=60  # Extended timeout
        )
        print("Database pool created successfully!")
        return pool
    except asyncpg.exceptions.ConnectionDoesNotExistError as e:
        print(f"Database does not exist: {e}")
    except asyncpg.exceptions.InvalidAuthorizationSpecificationError as e:
        print(f"Invalid credentials: {e}")
    except Exception as e:
        import traceback
        print(f"Failed to create database pool: {e}")
        traceback.print_exc()
        raise

# Example usage for testing
if __name__ == "__main__":
    import asyncio

    async def test_connection():
        try:
            pool = await create_db_pool()
            print("Connection pool created successfully!")
            # Test a simple query
            async with pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1;")
                print(f"Query result: {result}")
        except Exception as e:
            print(f"Error during database connection test: {e}")

    asyncio.run(test_connection())