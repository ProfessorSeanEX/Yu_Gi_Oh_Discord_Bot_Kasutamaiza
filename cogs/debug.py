"""
Debug commands for Kasutamaiza Bot.
- Tools for diagnostics and permission checking.
"""

import discord
from discord.ext import commands
from loguru import logger
from datetime import datetime, timezone  # Import datetime and timezone


class Debug(commands.Cog):
    """
    Debugging and diagnostic commands for the bot.
    Includes permission checking, diagnostics, and health tools.
    """

    # Class-level metadata
    __version__ = "1.0.1"
    __author__ = "ProfessorSeanEX"
    __description__ = "Provides tools for bot diagnostics and permission checking."

    category = "Debug"

    def __init__(self, bot, guild_id, token):
        """
        Initializes the Debug cog.
        """
        self.bot = bot
        self.guild_id = guild_id
        self.token = token  # Store TOKEN

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

    @discord.slash_command(name="diagnostics", description="Get full bot diagnostics and recent error logs.")
    async def slash_diagnostics(self, ctx: discord.ApplicationContext):
        """
        Provides full diagnostic information about the bot's state, environment, and recent errors.
        """
        logger.info(f"Diagnostics command triggered by {ctx.user}")
        await ctx.defer(ephemeral=True)  # Defer response to avoid timeouts

        # Collecting bot metadata
        bot_name = self.bot.user.name
        bot_id = self.bot.user.id
        total_commands = len(self.bot.application_commands)
        uptime = (
            str(datetime.now(timezone.utc) - self.bot.start_time).split(".")[0]
            if hasattr(self.bot, "start_time") else "Unknown"
        )

        # Categorizing commands
        guild_commands = [cmd.name for cmd in self.bot.application_commands if cmd.guild_ids]
        global_commands = [cmd.name for cmd in self.bot.application_commands if not cmd.guild_ids]

        # Checking permissions
        perms = ctx.guild.me.guild_permissions
        required_permissions = [
            "administrator", "manage_guild", "manage_roles",
            "send_messages", "manage_messages", "read_message_history", "manage_channels"
        ]
        missing_perms = [perm for perm in required_permissions if not getattr(perms, perm, False)]
        permissions_info = "✅ All required permissions are present." if not missing_perms else f"❌ Missing: {', '.join(missing_perms)}"

        # Loaded cogs
        loaded_cogs = "\n".join(f"- {cog}" for cog in self.bot.cogs.keys())

        # Environment variables
        environment_info = [
            "✅ `BOT_TOKEN` is set." if self.token else "❌ `BOT_TOKEN` is missing.",
            f"✅ `GUILD_ID`: `{self.guild_id}`" if self.guild_id else "❌ `GUILD_ID` is missing or invalid."
        ]

        # Formatting diagnostics response
        diagnostics_info = f"""
        **Bot Diagnostics**
        - **Name**: `{bot_name}`
        - **ID**: `{bot_id}`
        - **Uptime**: `{uptime}`
        - **Total Commands**: `{total_commands}`

        **Guild Slash Commands**
        {', '.join(guild_commands) if guild_commands else 'None'}

        **Global Slash Commands**
        {', '.join(global_commands) if global_commands else 'None'}

        **Permissions Check**
        {permissions_info}

        **Loaded Cogs**
        {loaded_cogs}

        **Environment Variables**
        {'\n'.join(environment_info)}
        """

        await ctx.followup.send(diagnostics_info, ephemeral=True)



def setup(bot: discord.Bot, guild_id: int, token: str):
    """
    Sets up the Debug cog by adding it to the bot.
    """
    logger.debug(f"Setting up Debug cog with guild_id: {guild_id}")
    bot.add_cog(Debug(bot, guild_id, token))
    logger.info(f"Debug cog has been added. Metadata: Version={Debug.__version__}, Author={Debug.__author__}")

    # Log the commands after setup
    logger.info("Registered commands after Debug cog setup:")
    for cmd in bot.application_commands:
        logger.info(
            f" - Command: {cmd.name} | Description: {cmd.description} | Guild ID(s): {cmd.guild_ids or 'Global'}"
        )