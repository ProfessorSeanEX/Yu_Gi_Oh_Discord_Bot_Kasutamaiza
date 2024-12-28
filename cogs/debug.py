import discord
from discord.ext import commands
import platform
import psutil
import time

class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()  # Track bot start time

    @discord.slash_command(description="Test database connectivity.", guild_ids=[551860536476827658])
    @commands.is_owner()
    async def testdb(self, ctx: discord.ApplicationContext):
        """Test database connectivity."""
        try:
            async with self.bot.db_pool.acquire() as conn:
                value = await conn.fetchval("SELECT 'Hello from PostgreSQL!'")
                await ctx.respond(f"DB says: {value}", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"Database error: {e}", ephemeral=True)

    @discord.slash_command(description="Show basic bot info.", guild_ids=[551860536476827658])
    @commands.is_owner()
    async def botinfo(self, ctx: discord.ApplicationContext):
        """Display debugging info."""
        try:
            latency = self.bot.latency * 1000
            memory = psutil.virtual_memory().percent
            uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.start_time))

            embed = discord.Embed(
                title="Bot Info",
                color=discord.Color.yellow()
            )
            embed.add_field(name="Latency", value=f"{latency:.2f} ms")
            embed.add_field(name="Memory Usage", value=f"{memory}%")
            embed.add_field(name="Uptime", value=uptime)
            embed.add_field(name="Cogs", value=", ".join(self.bot.cogs.keys()))

            await ctx.respond(embed=embed, ephemeral=True)
        except Exception as e:
            await ctx.respond(f"Error fetching bot info: {e}", ephemeral=True)

    @discord.slash_command(description="Echo a message for debugging.", guild_ids=[551860536476827658])
    @commands.is_owner()
    async def echo(self, ctx: discord.ApplicationContext, message: str):
        """Echo a message."""
        await ctx.respond(f"You said: {message}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DebugCog(bot))
