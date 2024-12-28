import os
import asyncio
import discord
from dotenv import load_dotenv
from db.db_connection import create_db_pool

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot using `discord.Bot`
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    try:
        await bot.sync_commands()  # Sync slash commands
        print("Slash commands synced.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

def load_cogs():
    """Synchronously load all cogs."""
    cogs_list = [
        "cogs.misc",
        "cogs.mod",
        "cogs.debug",  # Add more cogs as needed
    ]
    for cog in cogs_list:
        try:
            bot.load_extension(cog)  # No 'await' here
            print(f"Successfully loaded cog: {cog}")
        except Exception as e:
            print(f"Failed to load cog {cog}: {e}")

async def main():
    # Create a PostgreSQL connection pool for the bot
    try:
        bot.db_pool = await create_db_pool()
        print("Database connection pool established.")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return

    # Load cogs
    load_cogs()  # Synchronous function

    # Run the bot
    try:
        await bot.start(BOT_TOKEN)
    except Exception as e:
        print(f"Error starting the bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())