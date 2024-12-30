"""
General commands for Kasutamaiza Bot.
- Handles basic bot interactions and utilities.
"""

import discord
from discord.ext import commands
from loguru import logger
from datetime import datetime


class General(commands.Cog):
    """
    General commands for the bot, providing essential interactions such as health checks
    and help command access.
    """

    # Class-level metadata
    __version__ = "1.0.0"
    __author__ = "ProfessorSeanEX"
    __description__ = "Handles basic bot interactions and utilities."

    def __init__(self, bot, guild_id, token):
        """
        Initializes the General cog.
        """
        self.bot = bot
        self.guild_id = guild_id
        self.token = token
        self.start_time = discord.utils.utcnow()  # Track bot uptime

        # Dynamically update guild_ids for commands
        for cmd in self.__cog_commands__:
            if isinstance(cmd, discord.SlashCommand):
                cmd.guild_ids = [self.guild_id]

    def get_commands_by_category(self, category_name):
        """
        Fetch commands dynamically by category name.
        """
        commands_list = [
            f"- `/{cmd.name}`: {cmd.description}"
            for cmd in self.bot.application_commands
            if hasattr(cmd.cog, "category") and cmd.cog.category == category_name
        ]
        return "\n".join(commands_list) if commands_list else "No commands available."

    @discord.slash_command(name="ping", description="Check if the bot is online and view latency.")
    async def slash_ping(self, ctx: discord.ApplicationContext):
        """
        Slash command to check if the bot is online and display latency.
        """
        latency = round(self.bot.latency * 1000)  # Convert latency to milliseconds
        logger.info(f"Ping command triggered by {ctx.user}")
        await ctx.respond(f"Pong! Latency: {latency}ms.")

    @discord.slash_command(name="help", description="Display the help message.")
    async def slash_help(self, ctx: discord.ApplicationContext):
        """
        Displays a dynamic help message with all available commands organized by cog.
        Includes a quick-start guide for new users.
        """
        logger.info(f"Help command triggered by {ctx.user}")

        # Start building the help text
        help_text = "**Kasutamaiza Bot Commands**\n\n"

        # Quick-start guide
        help_text += (
            "**Quick Start**\n"
            "- Use `/ping` to check if the bot is online.\n"
            "- Use `/help` to see all commands.\n"
            "- Use `/card_lookup` to find Yu-Gi-Oh! cards.\n\n"
        )

        # Iterate through all cogs and their commands
        for cog_name, cog in self.bot.cogs.items():
            # Fetch cog description from docstring or fallback
            cog_description = cog.__doc__.strip() if cog.__doc__ else "No description available."
            help_text += f"**{cog_name}** - {cog_description}\n"

            # Get all commands in the cog
            cog_commands = [
                f"- `/{cmd.name}`: {cmd.description}"
                for cmd in self.bot.application_commands
                if cmd.cog_name == cog_name
            ]

            # Add commands or mention no commands are available
            if cog_commands:
                help_text += "\n".join(cog_commands) + "\n\n"
            else:
                help_text += "No commands available.\n\n"

        # Handle case with no cogs loaded
        if not self.bot.cogs:
            help_text += "No commands or cogs are currently loaded.\n\n"

        await ctx.respond(help_text)


    @discord.slash_command(name="uptime", description="Display the bot's uptime.")
    async def slash_uptime(self, ctx: discord.ApplicationContext):
        """
        Displays the bot's uptime since the last restart.
        """
        uptime = discord.utils.utcnow() - self.start_time
        uptime_str = str(uptime).split(".")[0]  # Remove microseconds
        logger.info(f"Uptime command triggered by {ctx.user}")
        await ctx.respond(f"**Uptime**: {uptime_str}")


def setup(bot: discord.Bot, guild_id: int, token: str):
    """
    Sets up the General cog by adding it to the bot.
    """
    logger.debug(f"Setting up General cog with guild_id: {guild_id}")
    bot.add_cog(General(bot, guild_id, token))
    logger.info(f"General cog has been added. Metadata: Version={General.__version__}, Author={General.__author__}")

    # Log the commands after setup
    logger.info("Registered commands after General cog setup:")
    for cmd in bot.application_commands:
        logger.info(
            f" - Command: {cmd.name} | Description: {cmd.description} | Guild ID(s): {cmd.guild_ids or 'Global'}"
        )
