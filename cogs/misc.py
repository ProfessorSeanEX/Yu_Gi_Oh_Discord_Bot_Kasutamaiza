# File: cogs/misc.py

import discord
from discord.ext import commands

class MiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="Check if the bot is alive.", guild_ids=[551860536476827658])  # Replace with your server ID
    async def ping(self, ctx: discord.ApplicationContext):
        """
        Responds with 'Pong!' to check bot responsiveness.
        """
        try:
            await ctx.respond("Pong!", ephemeral=True)  # Ephemeral response for cleanliness
        except Exception as e:
            await ctx.respond(f"An error occurred: {e}")
            print(f"Ping command error: {e}")  # Log error for debugging

    @discord.slash_command(description="Basic help command.", guild_ids=[551860536476827658])  # Replace with your server ID
    async def helpme(self, ctx: discord.ApplicationContext):
        """
        Displays a help message with a list of available commands.
        """
        try:
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
        except Exception as e:
            await ctx.respond(f"An error occurred: {e}")
            print(f"Helpme command error: {e}")  # Log error for debugging

async def setup(bot):
    await bot.add_cog(MiscCog(bot))