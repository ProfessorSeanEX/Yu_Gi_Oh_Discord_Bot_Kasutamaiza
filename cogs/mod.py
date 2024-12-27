import discord
from discord.ext import commands

class ModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(guild_only=True, description="Kick a user (Admin only).")
    @commands.has_permissions(kick_members=True)
    async def kick(
        self, 
        ctx: discord.ApplicationContext, 
        user: discord.Member, 
        reason: str = "No reason provided"
    ):
        try:
            await user.kick(reason=reason)
            await ctx.respond(f"{user.mention} has been kicked. Reason: {reason}")
        except discord.Forbidden:
            await ctx.respond("I don't have permission to kick that user.")
        except Exception as e:
            await ctx.respond(f"An error occurred: {e}")

    @discord.slash_command(guild_only=True, description="Ban a user (Admin only).")
    @commands.has_permissions(ban_members=True)
    async def ban(
        self, 
        ctx: discord.ApplicationContext, 
        user: discord.Member, 
        reason: str = "No reason provided"
    ):
        try:
            await user.ban(reason=reason)
            await ctx.respond(f"{user.mention} has been banned. Reason: {reason}")
        except discord.Forbidden:
            await ctx.respond("I don't have permission to ban that user.")
        except Exception as e:
            await ctx.respond(f"An error occurred: {e}")

def setup(bot):
    bot.add_cog(ModCog(bot))
