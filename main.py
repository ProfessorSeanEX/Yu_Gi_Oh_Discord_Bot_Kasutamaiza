import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from db.db_connection import create_db_pool

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    await bot.tree.sync()  # Sync slash commands
    print("Slash commands synced.")

async def load_cogs():
    cogs_list = [
        "cogs.misc",
        "cogs.mod",
        "cogs.debug",  # etc.
    ]
    for cog in cogs_list:
        await bot.load_extension(cog)
        
async def main():
    # Create a PG connection pool for the bot
    bot.db_pool = await create_db_pool()

    # Load cogs
    await load_cogs()

    # Run the bot
    await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
