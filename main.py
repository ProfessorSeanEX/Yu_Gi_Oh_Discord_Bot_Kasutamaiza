import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Create bot instance with a unique prefix
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Add this line
bot = commands.Bot(command_prefix=">>", intents=intents)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    print("Registered commands:", bot.commands)

# Event: Process all messages
@bot.event
async def on_message(message):
    # Log the received message
    print(f"Message received: {message.content}")
    
    # Ensure the bot doesn't respond to itself
    if message.author == bot.user:
        return

    # Process commands
    await bot.process_commands(message)

# Command: Ping
@bot.command(name="ping")
async def ping(ctx):
    print("Ping command triggered.")
    await ctx.send("Pong!")

# Run the bot
bot.run(TOKEN)