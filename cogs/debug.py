# File: cogs/debug.py

import discord
from discord.ext import commands

class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="Test database connectivity.")
    @commands.is_owner()
    async def testdb(self, ctx: discord.ApplicationContext):
        """
        Attempts to fetch a simple value from the database.
        Only bot owner can run this (for security).
        """
        async with self.bot.db_pool.acquire() as conn:
            value = await conn.fetchval("SELECT 'Hello from PostgreSQL!'")
            await ctx.respond(f"DB says: {value}")

    @discord.slash_command(description="Show basic bot info.")
    @commands.is_owner()
    async def botinfo(self, ctx: discord.ApplicationContext):
        """
        Displays some debugging info about the bot or environment.
        Only bot owner can run this for security reasons.
        """
        embed = discord.Embed(
            title="Bot Debug Info",
            description="List of basic commands:",
            color=discord.Color.yellow()
        )
        embed.add_field(name="/ping", value="Check bot responsiveness.", inline=False)
        embed.add_field(name="/helpme", value="Show this help message.", inline=False)
        embed.add_field(name="/kick", value="Kick a user (Admin only).", inline=False)
        embed.add_field(name="/ban", value="Ban a user (Admin only).", inline=False)
        await ctx.respond(embed=embed)

    @discord.slash_command(description="Echo a message for debugging.")
    @commands.is_owner()
    async def echo(self, ctx: discord.ApplicationContext, *, message: str):
        """
        Simple echo command to test slash command input or message parsing.
        Only bot owner can run this for security reasons.
        """
        await ctx.respond(f"You said: {message}")

async def setup(bot):
    await bot.add_cog(DebugCog(bot))