import discord
from discord.ext import commands

class ModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="Kick a user.", guild_ids=[551860536476827658])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: discord.ApplicationContext, user: discord.Member, reason: str = "No reason provided"):
        try:
            await user.kick(reason=reason)
            await ctx.respond(f"Kicked {user.mention}. Reason: {reason}")
        except Exception as e:
            await ctx.respond(f"Failed to kick user: {e}")

    @discord.slash_command(description="Ban a user.", guild_ids=[551860536476827658])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: discord.ApplicationContext, user: discord.Member, reason: str = "No reason provided"):
        try:
            await user.ban(reason=reason)
            await ctx.respond(f"Banned {user.mention}. Reason: {reason}")
        except Exception as e:
            await ctx.respond(f"Failed to ban user: {e}")

async def setup(bot):
    await bot.add_cog(ModCog(bot))

