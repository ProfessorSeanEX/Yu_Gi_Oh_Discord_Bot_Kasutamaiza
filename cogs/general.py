"""
General commands for Kasutamaiza Bot.
- Handles basic bot interactions and utilities.
"""

import discord
from discord.ext import commands
from discord.commands import slash_command
from loguru import logger

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
        logger.info(f"Ping command triggered by {ctx.author}")
        await ctx.send("Pong!")

    @slash_command(name="ping", description="Check if the bot is online.")
    async def slash_ping(self, ctx):
        """
        Slash command to check if the bot is online.
        """
        logger.info(f"Slash ping command triggered by {ctx.author}")
        await ctx.respond("Pong!")

    @commands.command(name="info")
    async def info(self, ctx):
        """
        Provides information about the bot.
        """
        logger.info(f"Info command triggered by {ctx.author}")
        bot_info = f"""
        **Kasutamaiza Bot**
        - Version: 1.0.0
        - Author: ProfessorSeanEX
        - Purpose: Enhance your Yu-Gi-Oh experience and server engagement.
        """
        await ctx.send(bot_info)

    @commands.command(name="help")
    async def help_command(self, ctx):
        """
        Displays a help message with available commands and their usage.
        """
        logger.info(f"Help command triggered by {ctx.author}")
        help_text = """
        **Kasutamaiza Bot Commands**

        **General Commands**
        - `>>ping`: Check if the bot is online.
        - `>>info`: Get information about the bot.
        - `/ping`: Slash command to check if the bot is online.
        - `>>help`: Display this help message.

        **Moderation Commands**
        - `>>kick @user [reason]`: Kick a member from the server.
        - `>>ban @user [reason]`: Ban a member from the server.

        **Yu-Gi-Oh Commands**
        - `>>dueling`: Links to DuelingBook for online dueling.
        """
        await ctx.send(help_text)

async def setup(bot):
    """
    Sets up the General cog by adding it to the bot.
    """
    bot.add_cog(General(bot))  # Remove `await`
