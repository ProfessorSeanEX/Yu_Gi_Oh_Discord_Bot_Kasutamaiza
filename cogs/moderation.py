"""
Moderation commands for Kasutamaiza Bot.
- Provides tools to manage the server (e.g., kick, ban, mute, warn, purge).
"""

import discord
from discord.ext import commands
from loguru import logger


class Moderation(commands.Cog):
    """
    Moderation commands for managing the server.
    Includes tools for user management and channel cleanup.
    """

    # Class-level metadata
    __version__ = "1.0.2"
    __author__ = "ProfessorSeanEX"
    __description__ = "Provides tools to manage server moderation tasks."

    category = "Moderation"

    def __init__(self, bot, guild_id, token):
        """
        Initializes the Moderation cog.
        """
        self.bot = bot
        self.guild_id = guild_id
        self.token = token

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

    @discord.slash_command(name="kick", description="Kick a member from the server.")
    @discord.default_permissions(kick_members=True)
    async def slash_kick(self, ctx: discord.ApplicationContext, member: discord.Member, reason: str = "No reason provided."):
        """
        Kick a member from the server.
        """
        logger.info(f"Kick command triggered by {ctx.user} on {member} with reason: {reason}")
        try:
            await member.kick(reason=reason)
            await ctx.respond(f"✅ {member} has been kicked for: {reason}")
        except discord.Forbidden:
            await ctx.respond("❌ I don't have permission to kick this member.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in kick command: {e}")
            await ctx.respond("❌ An error occurred while trying to kick the member.", ephemeral=True)

    @discord.slash_command(name="ban", description="Ban a member from the server.")
    @discord.default_permissions(ban_members=True)
    async def slash_ban(self, ctx: discord.ApplicationContext, member: discord.Member, reason: str = "No reason provided."):
        """
        Ban a member from the server.
        """
        logger.info(f"Ban command triggered by {ctx.user} on {member} with reason: {reason}")
        try:
            await member.ban(reason=reason)
            await ctx.respond(f"✅ {member} has been banned for: {reason}")
        except discord.Forbidden:
            await ctx.respond("❌ I don't have permission to ban this member.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in ban command: {e}")
            await ctx.respond("❌ An error occurred while trying to ban the member.", ephemeral=True)

    @discord.slash_command(name="mute", description="Mute a member temporarily.")
    @discord.default_permissions(manage_roles=True)
    async def slash_mute(self, ctx: discord.ApplicationContext, member: discord.Member, duration: int = 10, reason: str = "No reason provided."):
        """
        Temporarily mute a member.
        """
        logger.info(f"Mute command triggered by {ctx.user} on {member} for {duration} minutes with reason: {reason}")
        try:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if not muted_role:
                muted_role = await ctx.guild.create_role(name="Muted")
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, speak=False, send_messages=False)
            await member.add_roles(muted_role, reason=reason)
            await ctx.respond(f"✅ {member} has been muted for {duration} minutes: {reason}")
            
            # Automatically unmute after duration
            await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(minutes=duration))
            await member.remove_roles(muted_role, reason="Mute duration expired")
            logger.info(f"{member} has been automatically unmuted after {duration} minutes.")
        except Exception as e:
            logger.error(f"Error in mute command: {e}")
            await ctx.respond("❌ An error occurred while trying to mute the member.", ephemeral=True)

    @discord.slash_command(name="unmute", description="Unmute a member.")
    @discord.default_permissions(manage_roles=True)
    async def slash_unmute(self, ctx: discord.ApplicationContext, member: discord.Member):
        """
        Unmute a member.
        """
        logger.info(f"Unmute command triggered by {ctx.user} on {member}")
        try:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if muted_role in member.roles:
                await member.remove_roles(muted_role, reason="Unmuted by command")
                await ctx.respond(f"✅ {member} has been unmuted.")
            else:
                await ctx.respond(f"ℹ️ {member} is not currently muted.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in unmute command: {e}")
            await ctx.respond("❌ An error occurred while trying to unmute the member.", ephemeral=True)

    @discord.slash_command(name="purge", description="Delete multiple messages.")
    @discord.default_permissions(manage_messages=True)
    async def slash_purge(self, ctx: discord.ApplicationContext, amount: int):
        """
        Delete multiple messages from a channel.
        """
        logger.info(f"Purge command triggered by {ctx.user} to delete {amount} messages.")
        if amount <= 0 or amount > 100:
            await ctx.respond("❌ Please specify a number between 1 and 100.", ephemeral=True)
            return
        try:
            deleted = await ctx.channel.purge(limit=amount)
            await ctx.respond(f"✅ Deleted {len(deleted)} message(s).", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in purge command: {e}")
            await ctx.respond("❌ An error occurred while trying to delete messages.", ephemeral=True)

    @discord.slash_command(name="warn", description="Warn a member.")
    @discord.default_permissions(manage_messages=True)
    async def slash_warn(self, ctx: discord.ApplicationContext, member: discord.Member, reason: str = "No reason provided."):
        """
        Issue a warning to a member.
        """
        logger.info(f"Warn command triggered by {ctx.user} for {member} with reason: {reason}")
        try:
            await ctx.respond(f"⚠️ {member} has been warned: {reason}")
            logger.warning(f"Warning issued to {member}: {reason}")
        except Exception as e:
            logger.error(f"Error in warn command: {e}")
            await ctx.respond("❌ An error occurred while issuing the warning.", ephemeral=True)


def setup(bot: discord.Bot, guild_id: int, token: str):
    """
    Sets up the Moderation cog by adding it to the bot.
    """
    logger.debug(f"Setting up Moderation cog with guild_id: {guild_id}")
    bot.add_cog(Moderation(bot, guild_id, token))
    logger.info(f"Moderation cog has been added. Metadata: Version={Moderation.__version__}, Author={Moderation.__author__}")

    # Log the commands after setup
    logger.info("Registered commands after Moderation cog setup:")
    for cmd in bot.application_commands:
        logger.info(
            f" - Command: {cmd.name} | Description: {cmd.description} | Guild ID(s): {cmd.guild_ids or 'Global'}"
        )