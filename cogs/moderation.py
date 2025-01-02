"""
Moderation commands for Kasutamaiza Bot.
- Provides tools to manage the server (e.g., kick, ban, mute, warn, purge).

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX
- Purpose: Provide robust tools for server moderation tasks with enhanced modularity.
"""

import os
import logging
from datetime import datetime, timezone

# Import modules
import discord
from discord.ext import commands
from loguru import logger
from typing import Optional

# Utility imports
from utils import inject_helpers_into_namespace

# Inject all helpers into this module's global namespace
inject_helpers_into_namespace(globals())

logger = logging.getLogger(__name__)
class Moderation(commands.Cog):
    """
    Moderation commands for managing the server.
    Includes tools for user management, warnings, and channel cleanup.
    """

    # Class-level metadata
    __version__ = "1.0.0"
    __author__ = "ProfessorSeanEX"
    __description__ = "Provides tools to manage server moderation tasks and user warnings."
    category = "Moderation"

    def __init__(self, bot, guild_id, token):
        """
        Initializes the Moderation cog with guild-specific commands.
        """
        if not guild_id or not token:
            raise ValueError("guild_id and token must be provided for Moderation cog initialization.")

        self.bot = bot
        self.guild_id = guild_id
        self.token = token
        self.start_time = datetime.now(timezone.utc)
        for cmd in self.__cog_commands__:
            logger.debug(f"Registering command '{cmd.name}' to cog '{self.__class__.__name__}' with category '{self.category}'.")

        # Enforce category attribute
        if not hasattr(self, "category") or not isinstance(self.category, str):
            logger.warning(f"Cog '{self.__class__.__name__}' is missing a 'category' attribute. Defaulting to 'Uncategorized'.")
            self.category = "Uncategorized"

        # Assign guild_ids to commands dynamically
        for cmd in self.__cog_commands__:
            if isinstance(cmd, discord.SlashCommand):
                cmd.guild_ids = [self.guild_id]

        # Debugging log for validation
        logger.debug(f"Initializing {self.__class__.__name__} with category: {self.category}")
        logger.debug(f"{self.__class__.__name__} cog initialized with guild_id={self.guild_id}.")

    async def calculate_uptime(self) -> str:
        """
        Calculates the bot's uptime since initialization.

        Returns:
            str: Formatted uptime string.
        """
        uptime = datetime.now(timezone.utc) - self.start_time
        return str(uptime).split(".")[0]

    @discord.slash_command(name="kick", description="Kick a member from the server.")
    @discord.default_permissions(kick_members=True)
    async def slash_kick(self, ctx: discord.ApplicationContext, member: discord.Member, reason: str = "No reason provided."):
        """
        Kick a member from the server.
        """
        logger.info(f"Kick command triggered by {ctx.user} on {member} with reason: {reason}")
        permissions = validate_permissions(ctx, ["kick_members"])
        if not permissions["has_all"]:
            await format_embed_response(ctx, title="Permission Denied", fields={"Missing Permissions": ", ".join(permissions["missing"])}, color=discord.Color.red(), ephemeral=True)
            return

        try:
            await member.kick(reason=reason)
            fields = {"Member": str(member), "Reason": reason}
            await format_embed_response(ctx, title="Member Kicked", fields=fields)
        except discord.Forbidden:
            await format_embed_response(ctx, title="Permission Denied", fields={"Message": "I don't have permission to kick this member."}, color=discord.Color.red(), ephemeral=True)
        except Exception as e:
            logger.error(f"Error in kick command: {e}")
            await format_embed_response(ctx, title="Error", fields={"Message": "An error occurred while trying to kick the member."}, color=discord.Color.red(), ephemeral=True)

    @discord.slash_command(name="ban", description="Ban a member from the server.")
    @discord.default_permissions(ban_members=True)
    async def slash_ban(self, ctx: discord.ApplicationContext, member: discord.Member, reason: str = "No reason provided."):
        """
        Ban a member from the server.
        """
        logger.info(f"Ban command triggered by {ctx.user} on {member} with reason: {reason}")
        permissions = validate_permissions(ctx, ["ban_members"])
        if not permissions["has_all"]:
            await format_embed_response(ctx, title="Permission Denied", fields={"Missing Permissions": ", ".join(permissions["missing"])}, color=discord.Color.red(), ephemeral=True)
            return

        try:
            await member.ban(reason=reason)
            fields = {"Member": str(member), "Reason": reason}
            await format_embed_response(ctx, title="Member Banned", fields=fields)
        except discord.Forbidden:
            await format_embed_response(ctx, title="Permission Denied", fields={"Message": "I don't have permission to ban this member."}, color=discord.Color.red(), ephemeral=True)
        except Exception as e:
            logger.error(f"Error in ban command: {e}")
            await format_embed_response(ctx, title="Error", fields={"Message": "An error occurred while trying to ban the member."}, color=discord.Color.red(), ephemeral=True)

    @discord.slash_command(name="mute", description="Mute a member temporarily.")
    @discord.default_permissions(manage_roles=True)
    async def slash_mute(self, ctx: discord.ApplicationContext, member: discord.Member, duration: int = 10, reason: str = "No reason provided."):
        """
        Temporarily mute a member.
        """
        logger.info(f"Mute command triggered by {ctx.user} on {member} for {duration} minutes with reason: {reason}")
        permissions = validate_permissions(ctx, ["manage_roles"])
        if not permissions["has_all"]:
            await format_embed_response(ctx, title="Permission Denied", fields={"Missing Permissions": ", ".join(permissions["missing"])}, color=discord.Color.red(), ephemeral=True)
            return

        try:
            # Ensure the "Muted" role exists
            muted_role = await ensure_role_exists(ctx, "Muted", permissions=discord.Permissions(send_messages=False, speak=False))
            await assign_role(member, muted_role)

            fields = {"Member": str(member), "Duration": f"{duration} minutes", "Reason": reason}
            await format_embed_response(ctx, title="Member Muted", fields=fields)

            # Schedule automatic unmute
            async def auto_unmute():
                await asyncio.sleep(duration * 60)
                await remove_role(member, muted_role)
                logger.info(f"{member} has been automatically unmuted after {duration} minutes.")

            ctx.bot.loop.create_task(auto_unmute())
        except Exception as e:
            logger.error(f"Error in mute command: {e}")
            await format_embed_response(ctx, title="Error", fields={"Message": "An error occurred while trying to mute the member."}, color=discord.Color.red(), ephemeral=True)

    @discord.slash_command(name="unmute", description="Unmute a member.")
    @discord.default_permissions(manage_roles=True)
    async def slash_unmute(self, ctx: discord.ApplicationContext, member: discord.Member):
        """
        Unmute a member.
        """
        logger.info(f"Unmute command triggered by {ctx.user} on {member}")
        permissions = validate_permissions(ctx, ["manage_roles"])
        if not permissions["has_all"]:
            await format_embed_response(ctx, title="Permission Denied", fields={"Missing Permissions": ", ".join(permissions["missing"])}, color=discord.Color.red(), ephemeral=True)
            return

        try:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if not muted_role:
                await format_embed_response(ctx, title="Role Not Found", fields={"Message": "No 'Muted' role exists in this server."}, color=discord.Color.orange(), ephemeral=True)
                return

            await remove_role(member, muted_role)
            await format_embed_response(ctx, title="Member Unmuted", fields={"Member": str(member)})
        except Exception as e:
            logger.error(f"Error in unmute command: {e}")
            await format_embed_response(ctx, title="Error", fields={"Message": "An error occurred while trying to unmute the member."}, color=discord.Color.red(), ephemeral=True)

    @discord.slash_command(name="purge", description="Delete multiple messages.")
    @discord.default_permissions(manage_messages=True)
    async def slash_purge(self, ctx: discord.ApplicationContext, amount: int):
        """
        Delete multiple messages from a channel.
        """
        logger.info(f"Purge command triggered by {ctx.user} to delete {amount} messages.")
        if amount <= 0 or amount > 100:
            await format_embed_response(ctx, title="Invalid Amount", fields={"Message": "Please specify a number between 1 and 100."}, color=discord.Color.red(), ephemeral=True)
            return
        try:
            deleted = await ctx.channel.purge(limit=amount)
            fields = {"Deleted Messages": len(deleted)}
            await format_embed_response(ctx, title="Purge Successful", fields=fields, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in purge command: {e}")
            await format_embed_response(ctx, title="Error", fields={"Message": "An error occurred while trying to delete messages."}, color=discord.Color.red(), ephemeral=True)


async def setup(bot: discord.Bot, guild_id: Optional[int] = None, token: Optional[str] = None):
    """
    Sets up the Moderation cog by adding it to the bot.
    """
    logger.debug("Initializing Moderation cog setup...")

    # Fetch environment variables if not explicitly provided
    guild_id = guild_id or int(os.getenv("GUILD_ID", 0))
    token = token or os.getenv("BOT_TOKEN", "")

    # Validate environment variables
    if guild_id == 0 or not token:
        logger.error("GUILD_ID or BOT_TOKEN environment variable is not set or invalid.")
        return

    try:
        # Add cog to the bot
        cog = Moderation(bot, guild_id, token)
        bot.add_cog(cog)
        logger.info(f"Moderation cog successfully loaded for guild {guild_id}.")
        logger.info(f"Metadata: Version={Moderation.__version__}, Author={Moderation.__author__}")

        # Do not call sync_commands here; defer to on_ready
        logger.debug("Skipping sync_commands during setup. Will be handled in on_ready.")
    except Exception as e:
        logger.error(f"Failed to setup Moderation cog: {e}")

        # Log registered commands after setup
        if bot.application_commands:
            logger.info("Registered commands after Moderation cog setup:")
            for cmd in bot.application_commands:
                logger.info(f" - Command: {cmd.name} | Description: {cmd.description} | Guild ID(s): {cmd.guild_ids or 'Global'}")
        else:
            logger.warning("No commands found in bot.application_commands after cog setup.")
