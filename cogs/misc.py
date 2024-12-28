# File: cogs/misc.py

import discord
from discord.ext import commands

class MiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="Check if the bot is alive.")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond("Pong!")

    @discord.slash_command(description="Basic help command.")
    async def helpme(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="Help",
            description="List of basic commands:",
            color=discord.Color.blue()
        )
        embed.add_field(name="/ping", value="Check bot responsiveness.", inline=False)
        embed.add_field(name="/helpme", value="Show this help message.", inline=False)
        embed.add_field(name="/kick", value="Kick a user (Admin only).", inline=False)
        embed.add_field(name="/ban", value="Ban a user (Admin only).", inline=False)
        await ctx.respond(embed=embed)

async def setup(bot):
    await bot.add_cog(MiscCog(bot))