import discord
from discord.ext import commands

class MiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="Check bot latency.", guild_ids=[551860536476827658])
    async def ping(self, ctx: discord.ApplicationContext):
        latency = self.bot.latency * 1000
        await ctx.respond(f"Pong! Latency: {latency:.2f} ms", ephemeral=True)

    @discord.slash_command(description="Show help.", guild_ids=[551860536476827658])
    async def helpme(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="Help",
            description="Available commands:",
            color=discord.Color.blue()
        )
        embed.add_field(name="/ping", value="Check bot latency.")
        embed.add_field(name="/helpme", value="Show this help.")
        embed.add_field(name="/kick", value="Kick a user.")
        embed.add_field(name="/ban", value="Ban a user.")
        await ctx.respond(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(MiscCog(bot))
