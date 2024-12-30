"""
Utility commands for Kasutamaiza Bot.
- Provides bot-related information and server details.
"""

import discord
from discord.ext import commands
from loguru import logger


class Utility(commands.Cog):
    """
    Utility commands for the bot.
    Provides metadata, server details, and other useful utilities.
    """

    # Class-level metadata
    __version__ = "1.0.1"
    __author__ = "ProfessorSeanEX"
    __description__ = "Provides bot-related information and server details."

    category = "Utility"

    def __init__(self, bot, guild_id, token):
        """
        Initializes the Utility cog.
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

    @discord.slash_command(name="info", description="Provides information about the bot.")
    async def slash_info(self, ctx: discord.ApplicationContext):
        """
        Provides metadata and general information about the bot.
        """
        logger.info(f"Info command triggered by {ctx.user}")
        bot_info = f"""
        **Kasutamaiza Bot Metadata**
        - Version: {self.__version__}
        - Author: {self.__author__}
        - Purpose: Enhance your Yu-Gi-Oh experience and server engagement.
        - Total Commands: {len(self.bot.application_commands)}
        - Connected Guild: {ctx.guild.name} (ID: {ctx.guild.id})
        """
        await ctx.respond(bot_info)

    @discord.slash_command(name="server_info", description="Provides information about the current server.")
    async def slash_server_info(self, ctx: discord.ApplicationContext):
        """
        Provides information about the server.
        """
        logger.info(f"Server info command triggered by {ctx.user}")
        guild = ctx.guild
        member_count = guild.member_count
        creation_date = guild.created_at.strftime('%Y-%m-%d %H:%M:%S')
        server_info = f"""
        **Server Information**
        - Name: `{guild.name}`
        - ID: `{guild.id}`
        - Owner: `{guild.owner}`
        - Members: `{member_count}`
        - Created At: `{creation_date}`
        """
        await ctx.respond(server_info)

    @discord.slash_command(name="bot_status", description="Provides the bot's current status.")
    async def slash_bot_status(self, ctx: discord.ApplicationContext):
        """
        Displays the bot's online status and latency.
        """
        latency = round(self.bot.latency * 1000)  # Convert latency to milliseconds
        logger.info(f"Bot status command triggered by {ctx.user}")
        await ctx.respond(f"**Bot Status**: Online\n**Latency**: {latency}ms")

    @discord.slash_command(name="get_invite", description="Get the bot's invite link for other servers.")
    async def slash_get_invite(self, ctx: discord.ApplicationContext):
        """
        Provides an invite link to add the bot to other servers.
        """
        permissions = discord.Permissions(
            administrator=True  # Adjust permissions as needed
        )
        invite_url = discord.utils.oauth_url(client_id=self.bot.user.id, permissions=permissions)
        logger.info(f"Invite link command triggered by {ctx.user}")
        await ctx.respond(f"**Invite Kasutamaiza Bot**:\n{invite_url}")


def setup(bot: discord.Bot, guild_id: int, token: str):
    """
    Sets up the Utility cog by adding it to the bot.
    """
    logger.debug(f"Setting up Utility cog with guild_id: {guild_id}")
    bot.add_cog(Utility(bot, guild_id, token))
    logger.info(f"Utility cog has been added. Metadata: Version={Utility.__version__}, Author={Utility.__author__}")

    # Log the commands after setup
    logger.info("Registered commands after Utility cog setup:")
    for cmd in bot.application_commands:
        logger.info(
            f" - Command: {cmd.name} | Description: {cmd.description} | Guild ID(s): {cmd.guild_ids or 'Global'}"
        )