import os
import asyncio
import asyncpg
import ssl
from loguru import logger
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
SSL_CERT_PATH = os.getenv("SSL_CERT_PATH", None)  # Path to CA certificate file if provided

# Validate environment variables
missing_vars = [var for var in ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"] if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

# Convert DB_PORT to integer
DB_PORT = int(DB_PORT)

# Configure SSL if required
ssl_context = None
if USE_SSL:
    if SSL_CERT_PATH:
        if not os.path.isfile(SSL_CERT_PATH):
            logger.error(f"SSL certificate file not found at: {SSL_CERT_PATH}")
            raise FileNotFoundError(f"Certificate file not found: {SSL_CERT_PATH}")
        logger.info(f"Using SSL with custom CA certificate: {SSL_CERT_PATH}")
        ssl_context = ssl.create_default_context(cafile=SSL_CERT_PATH)
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = True
    else:
        logger.info("Using SSL with default system CA certificates.")
        ssl_context = ssl.create_default_context()
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = True

    if os.getenv("DISABLE_SSL_VERIFICATION", "False").lower() in ("true", "1", "yes"):
        logger.warning("SSL verification disabled! Not secure for production.")
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

async def create_db_pool(retries=3, delay=5):
    """Create and return a global connection pool for PostgreSQL."""
    for attempt in range(retries):
        try:
            logger.info(f"Attempting connection to {DB_HOST}:{DB_PORT} with SSL={USE_SSL}")
            pool = await asyncpg.create_pool(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                ssl=ssl_context,
                timeout=DB_TIMEOUT,
                min_size=1,
                max_size=5
            )
            logger.info("Database pool created successfully!")
            return pool
        except Exception as e:
            logger.error(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.critical("All connection attempts failed.")
                raise