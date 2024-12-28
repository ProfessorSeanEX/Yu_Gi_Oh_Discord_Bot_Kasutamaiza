import os
import asyncpg
import ssl
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
SSL_CERT_PATH = os.getenv("SSL_CERT_PATH", None)  # Path to CA certificate file if provided
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "yes")

# Debugging logs
if DEBUG_MODE:
    logger.debug("Debug mode is enabled.")
    logger.debug(f"DB_HOST: {DB_HOST}, DB_PORT: {DB_PORT}, DB_USER: {DB_USER}")
    logger.debug(f"SSL_CERT_PATH: {SSL_CERT_PATH}, USE_SSL: {USE_SSL}, DISABLE_SSL_VERIFICATION: {os.getenv('DISABLE_SSL_VERIFICATION')}")

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

# Validate SSL_CERT_PATH
if USE_SSL and SSL_CERT_PATH:
    if not os.path.isfile(SSL_CERT_PATH):
        raise FileNotFoundError(f"SSL certificate file not found at: {SSL_CERT_PATH}")

# Configure SSL if required
ssl_context = None
if USE_SSL:
    if SSL_CERT_PATH:
        logger.info(f"Using SSL with custom CA certificate: {SSL_CERT_PATH}")
        ssl_context = ssl.create_default_context(cafile=SSL_CERT_PATH)
        ssl_context.verify_mode = ssl.CERT_REQUIRED
    else:
        logger.info("Using SSL with default system CA certificates.")
        ssl_context = ssl.create_default_context()

    # Optional: For testing, completely disable SSL verification
    if os.getenv("DISABLE_SSL_VERIFICATION", "False").lower() in ("true", "1", "yes"):
        logger.warning("SSL verification disabled! This is not secure and should not be used in production.")
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

async def create_db_pool():
    """Create and return a global connection pool for PostgreSQL."""
    try:
        logger.info(f"Attempting connection to {DB_HOST}:{DB_PORT} with SSL={USE_SSL}")
        pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            ssl=ssl_context,
            timeout=DB_TIMEOUT
        )
        logger.info("Database pool created successfully!")
        return pool
    except asyncpg.exceptions.ConnectionDoesNotExistError as e:
        logger.error(f"Database does not exist: {e}")
    except asyncpg.exceptions.InvalidAuthorizationSpecificationError as e:
        logger.error(f"Invalid credentials: {e}")
    except ssl.SSLError as e:
        logger.error(f"SSL error: {e}")
    except Exception as e:
        import traceback
        logger.error(f"Failed to create database pool: {e}")
        traceback.print_exc()
        raise

# Example usage for testing
if __name__ == "__main__":
    import asyncio

    async def test_connection():
        try:
            pool = await create_db_pool()
            logger.info("Connection pool created successfully!")
            # Test a simple query
            async with pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1;")
                logger.info(f"Query result: {result}")
        except Exception as e:
            logger.error(f"Error during database connection test: {e}")

    asyncio.run(test_connection())