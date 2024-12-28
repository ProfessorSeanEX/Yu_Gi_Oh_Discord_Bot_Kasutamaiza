# File: cogs/mod.py

import discord
from discord.ext import commands

class ModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

@commands.guild_only()
@discord.slash_command(description="Kick a user (Admin only).", guild_ids=[551860536476827658])  # Replace with your server ID
@commands.has_permissions(kick_members=True)
async def kick(
    self,
    ctx: discord.ApplicationContext,
    user: discord.Member,
    reason: str = "No reason provided"
):
    """
    Kicks a user from the guild.
    Only users with Kick Members permission can use this command.
    """
    if not ctx.guild:  # Ensure the command is used in a guild
        await ctx.respond("This command can only be used in a server.", ephemeral=True)
        return

    try:
        await user.kick(reason=reason)
        await ctx.respond(f"{user.mention} has been kicked. Reason: {reason}")
    except discord.Forbidden:
        await ctx.respond("I don't have permission to kick that user.")
    except Exception as e:
        await ctx.respond(f"An error occurred: {e}")
        print(f"Kick command error: {e}")  # Log error for debugging

@commands.guild_only()
@discord.slash_command(description="Ban a user (Admin only).", guild_ids=[551860536476827658])  # Replace with your server ID
@commands.has_permissions(ban_members=True)
async def ban(
    self,
    ctx: discord.ApplicationContext,
    user: discord.Member,
    reason: str = "No reason provided"
):
    """
    Bans a user from the guild.
    Only users with Ban Members permission can use this command.
    """
    if not ctx.guild:  # Ensure the command is used in a guild
        await ctx.respond("This command can only be used in a server.", ephemeral=True)
        return

    try:
        await user.ban(reason=reason)
        await ctx.respond(f"{user.mention} has been banned. Reason: {reason}")
    except discord.Forbidden:
        await ctx.respond("I don't have permission to ban that user.")
    except Exception as e:
        await ctx.respond(f"An error occurred: {e}")
        print(f"Ban command error: {e}")  # Log error for debugging

async def setup(bot):
    await bot.add_cog(ModCog(bot))
