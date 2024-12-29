"""
Moderation commands for Kasutamaiza Bot.
- Provides tools to manage the server (e.g., kick, ban).
"""

import discord
from discord.ext import commands

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
        try:
            await member.kick(reason=reason)
            await ctx.send(f"Member {member} has been kicked.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick this member.")

    @commands.command(name="ban")
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """
        Ban a member from the server.
        """
        try:
            await member.ban(reason=reason)
            await ctx.send(f"Member {member} has been banned.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to ban this member.")

async def setup(bot):
    """
    Sets up the Moderation cog by adding it to the bot.
    """
    await bot.add_cog(Moderation(bot))