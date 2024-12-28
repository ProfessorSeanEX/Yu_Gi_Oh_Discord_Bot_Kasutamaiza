import discord
from discord.ext import commands
import platform
import psutil  # To monitor system resource usage
import time

class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()  # Track bot start time

    @discord.slash_command(description="Test database connectivity.", guild_ids=[551860536476827658])  # Replace with your server ID
    @commands.is_owner()
    async def testdb(self, ctx: discord.ApplicationContext):
        """
        Attempts to fetch a simple value from the database.
        Only bot owner can run this (for security).
        """
        try:
            async with self.bot.db_pool.acquire() as conn:
                value = await conn.fetchval("SELECT 'Hello from PostgreSQL!'")
                await ctx.respond(f"DB says: {value}", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"An error occurred: {e}", ephemeral=True)
            print(f"testdb command error: {e}")  # Log error for debugging

    @discord.slash_command(description="Show basic bot info.", guild_ids=[551860536476827658])  # Replace with your server ID
    @commands.is_owner()
    async def botinfo(self, ctx: discord.ApplicationContext):
        """
        Displays debugging info about the bot or environment.
        Only bot owner can run this for security reasons.
        """
        try:
            # Gather debugging info
            system_info = platform.platform()
            python_version = platform.python_version()
            memory_usage = psutil.virtual_memory().percent
            uptime_seconds = time.time() - self.start_time
            uptime_formatted = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

            embed = discord.Embed(
                title="Bot Debug Info",
                color=discord.Color.yellow()
            )
            embed.add_field(name="Python Version", value=python_version, inline=False)
            embed.add_field(name="System Info", value=system_info, inline=False)
            embed.add_field(name="Memory Usage", value=f"{memory_usage}%", inline=False)
            embed.add_field(name="Bot Uptime", value=uptime_formatted, inline=False)
            embed.add_field(name="Loaded Cogs", value=f"{', '.join(self.bot.cogs.keys())}", inline=False)

            await ctx.respond(embed=embed, ephemeral=True)
        except Exception as e:
            await ctx.respond(f"An error occurred: {e}", ephemeral=True)
            print(f"botinfo command error: {e}")  # Log error for debugging

    @discord.slash_command(description="Echo a message for debugging.", guild_ids=[551860536476827658])  # Replace with your server ID
    @commands.is_owner()
    async def echo(self, ctx: discord.ApplicationContext, *, message: str):
        """
        Simple echo command to test slash command input or message parsing.
        Only bot owner can run this for security reasons.
        """
        try:
            await ctx.respond(f"You said: {message}", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"An error occurred: {e}", ephemeral=True)
            print(f"echo command error: {e}")  # Log error for debugging

async def setup(bot):
    await bot.add_cog(DebugCog(bot))