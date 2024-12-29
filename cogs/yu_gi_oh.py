"""
Yu-Gi-Oh-specific commands for Kasutamaiza Bot.
"""

import discord
from discord.ext import commands
from loguru import logger

class YuGiOh(commands.Cog):
    """Yu-Gi-Oh-specific commands for the bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dueling")
    async def dueling(self, ctx):
        """
        Provides a link to DuelingBook for online dueling.
        """
        logger.info(f"Dueling command triggered by {ctx.author}")
        dueling_link = "https://www.duelingbook.com/"
        await ctx.send(f"Ready to duel? Visit DuelingBook here: {dueling_link}")

async def setup(bot):
    """
    Sets up the Yu-Gi-Oh cog by adding it to the bot.
    """
    bot.add_cog(YuGiOh(bot))  # Remove `await`