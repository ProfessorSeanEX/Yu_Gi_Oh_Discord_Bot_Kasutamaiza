"""
General commands for Kasutamaiza Bot.
- Handles basic bot interactions and utilities.
"""

import discord
from discord.ext import commands
from loguru import logger


class General(commands.Cog):
    """General commands for the bot."""

    # Class-level attribute for command categorization
    category = "General"

    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild_id = guild_id

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

    @discord.slash_command(name="ping", description="Check if the bot is online.")
    async def slash_ping(self, ctx: discord.ApplicationContext):
        """
        Slash command to check if the bot is online.
        """
        logger.info(f"Slash ping command triggered by {ctx.user}")
        await ctx.respond("Pong!")

    @discord.slash_command(name="info", description="Provides information about the bot.")
    async def slash_info(self, ctx: discord.ApplicationContext):
        """
        Provides information about the bot.
        """
        logger.info(f"Info command triggered by {ctx.user}")
        bot_info = f"""
        **Kasutamaiza Bot**
        - Version: 1.0.0
        - Author: ProfessorSeanEX
        - Purpose: Enhance your Yu-Gi-Oh experience and server engagement.
        """
        await ctx.respond(bot_info)

    @discord.slash_command(name="help", description="Display the help message.")
    async def slash_help(self, ctx: discord.ApplicationContext):
        """
        Displays a help message with available commands and their usage.
        """
        logger.info(f"Help command triggered by {ctx.user}")

        general_commands = self.get_commands_by_category("General")
        moderation_commands = self.get_commands_by_category("Moderation")
        yugioh_commands = self.get_commands_by_category("Yu-Gi-Oh")

        help_text = f"""
        **Kasutamaiza Bot Commands**

        **General Commands**
        {general_commands}

        **Moderation Commands**
        {moderation_commands}

        **Yu-Gi-Oh Commands**
        {yugioh_commands}
        """
        await ctx.respond(help_text)

    @discord.slash_command(name="check_permissions", description="Check the bot's permissions in the current channel.")
    async def slash_check_permissions(self, ctx: discord.ApplicationContext):
        """
        Checks the bot's permissions in the current channel.
        """
        perms = ctx.guild.me.guild_permissions
        permission_list = [
            "manage_guild",  # Manage Server
            "administrator",  # Admin rights
            "manage_roles",
            "send_messages",
            "manage_messages",
            "read_message_history",
            "manage_channels",
        ]
        result = {perm: getattr(perms, perm, False) for perm in permission_list}
        logger.info(f"Permissions checked in {ctx.guild.name}: {result}")
        await ctx.respond(f"Permissions:\n{result}")

    @discord.slash_command(name="diagnostics", description="Get bot diagnostics information.")
    async def slash_diagnostics(self, ctx: discord.ApplicationContext):
        """
        Provides diagnostic information about the bot's state.
        """
        logger.info(f"Diagnostics command triggered by {ctx.user}")

        # Collect basic information
        diagnostics_info = f"""
        **Bot Diagnostics**
        - Name: {self.bot.user.name}
        - ID: {self.bot.user.id}
        - Connected Guild: {ctx.guild.name} (ID: {ctx.guild.id})
        - Total Slash Commands: {len(self.bot.application_commands)}
        - Guild Slash Commands: {', '.join(cmd.name for cmd in self.bot.application_commands if cmd.guild_ids)}
        - Global Slash Commands: {', '.join(cmd.name for cmd in self.bot.application_commands if not cmd.guild_ids)}
        """

        # Permissions
        perms = ctx.guild.me.guild_permissions
        missing_perms = [
            perm for perm in [
                "administrator",
                "manage_guild",
                "manage_roles",
                "send_messages",
                "manage_messages",
                "read_message_history",
                "manage_channels",
            ]
            if not getattr(perms, perm, False)
        ]
        permissions_info = "All required permissions are present." if not missing_perms else f"Missing permissions: {', '.join(missing_perms)}"

        # Final response
        diagnostics_info += f"\n\n**Permissions Check**\n{permissions_info}"
        logger.info(f"Diagnostics Info:\n{diagnostics_info}")
        await ctx.respond(diagnostics_info)


def setup(bot: discord.Bot, guild_id: int):
    """
    Sets up the General cog by adding it to the bot.
    """
    logger.debug(f"Setting up General cog with guild_id: {guild_id}")
    bot.add_cog(General(bot, guild_id))
    logger.info("General cog has been added.")

    # Log the commands after setup
    logger.info("Registered commands after General cog setup:")
    for cmd in bot.application_commands:
        logger.info(
            f" - Command: {cmd.name} | Description: {cmd.description} | Guild ID(s): {cmd.guild_ids or 'Global'}"
        )