"""
Moderation commands for Kasutamaiza Bot.
- Provides tools to manage the server (e.g., kick, ban).
"""

import discord
from discord.ext import commands
from loguru import logger

# Metadata
__category__ = "Moderation Commands"
__commands__ = ["kick", "ban"]

class Moderation(commands.Cog):
    """Moderation commands for managing the server."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kick")
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """
        Kick a member from the server.
        """
        logger.info(f"Kick command triggered by {ctx.author} on {member} with reason: {reason}")
        try:
            await member.kick(reason=reason)
            await ctx.send(f"Member {member} has been kicked.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick this member.")
        except Exception as e:
            logger.error(f"Error in kick command: {e}")
            await ctx.send("An error occurred while trying to kick the member.")

    @commands.command(name="ban")
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """
        Ban a member from the server.
        """
        logger.info(f"Ban command triggered by {ctx.author} on {member} with reason: {reason}")
        try:
            await member.ban(reason=reason)
            await ctx.send(f"Member {member} has been banned.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to ban this member.")
        except Exception as e:
            logger.error(f"Error in ban command: {e}")
            await ctx.send("An error occurred while trying to ban the member.")

async def setup(bot):
    """
    Sets up the Moderation cog by adding it to the bot.
    """
    bot.add_cog(Moderation(bot))  # Remove `await`