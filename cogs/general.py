"""
General commands for Kasutamaiza Bot.
- Handles basic bot interactions and utilities.
"""

import discord
from discord.ext import commands
from discord.commands import slash_command

# Metadata
__category__ = "General Commands"
__commands__ = ["ping", "info", "help"]

class General(commands.Cog):
    """General commands for the bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """
        Check if the bot is online.
        Responds with 'Pong!'.
        """
        await ctx.send("Pong!")

    @slash_command(name="ping", description="Check if the bot is online.")
    async def slash_ping(self, ctx):
        """
        Slash command to check if the bot is online.
        """
        await ctx.respond("Pong!")

    @commands.command(name="info")
    async def info(self, ctx):
        """
        Provides information about the bot.
        """
        bot_info = f"""
        **Kasutamaiza Bot**
        - Version: {__version__}
        - Author: {__author__}
        - Purpose: {__purpose__}
        """
        await ctx.send(bot_info)

    @commands.command(name="help")
    async def help_command(self, ctx):
        """
        Displays a help message with available commands.
        """
        help_text = """
        **Kasutamaiza Bot Commands**
        - `>>ping`: Check if the bot is online.
        - `>>info`: Get information about the bot.
        - `/ping`: Slash command to check if the bot is online.
        """
        await ctx.send(help_text)

async def setup(bot):
    """
    Sets up the General cog by adding it to the bot.
    """
    await bot.add_cog(General(bot))