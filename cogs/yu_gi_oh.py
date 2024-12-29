"""
Yu-Gi-Oh-specific commands for Kasutamaiza Bot.
"""

import discord
from discord.ext import commands
from loguru import logger
import requests  # Required for the card lookup command

class YuGiOh(commands.Cog):
    """Yu-Gi-Oh-specific commands for the bot."""

    # Class-level attribute for command categorization
    category = "Yu-Gi-Oh"

    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild_id = guild_id

        # Dynamically update guild_ids for commands
        for cmd in self.__cog_commands__:
            if isinstance(cmd, discord.SlashCommand):
                cmd.guild_ids = [self.guild_id]

    def get_commands_by_category(self, category_name):
        """
        Fetch commands dynamically by category name.
        """
        commands_list = [
            f"- `/{cmd.name}`: {cmd.description}"
            for cmd in self.bot.application_commands
            if hasattr(cmd.cog, "category") and cmd.cog.category == category_name
        ]
        return "\n".join(commands_list) if commands_list else "No commands available."

    @discord.slash_command(name="dueling", description="Get a link to DuelingBook for online dueling.")
    async def slash_dueling(self, ctx: discord.ApplicationContext):
        """
        Provides a link to DuelingBook for online dueling.
        """
        logger.info(f"Dueling command triggered by {ctx.user}")
        dueling_link = "https://www.duelingbook.com/"
        await ctx.respond(f"Ready to duel? Visit DuelingBook here: {dueling_link}")

    @discord.slash_command(name="card_lookup", description="Look up a Yu-Gi-Oh! card by name.")
    async def slash_card_lookup(self, ctx: discord.ApplicationContext, card_name: str):
        """
        Fetches card information from the YGOPRODeck API.
        """
        logger.info(f"Card lookup command triggered by {ctx.user} for card: {card_name}")
        from urllib.parse import quote

        card_name_encoded = quote(card_name)  # Ensure proper URL encoding
        api_url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={card_name_encoded}"

        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            data = response.json()
            if "data" not in data:
                await ctx.respond(f"No card found with the name '{card_name}'.", ephemeral=True)
                return

            card = data["data"][0]  # Fetch the first matching card
            embed = discord.Embed(
                title=card["name"],
                description=card.get("desc", "No description available."),
                color=discord.Color.blue(),
            )
            embed.add_field(name="Type", value=card.get("type", "Unknown"), inline=True)
            embed.add_field(name="Race", value=card.get("race", "Unknown"), inline=True)
            embed.add_field(name="Attribute", value=card.get("attribute", "Unknown"), inline=True)
            embed.set_thumbnail(url=card.get("card_images", [{}])[0].get("image_url", ""))

            await ctx.respond(embed=embed)
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e} for URL: {api_url}")
            await ctx.respond("Failed to fetch card data. Please check the card name or try again later.", ephemeral=True)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Exception: {e}")
            await ctx.respond("Failed to connect to the card database. Please try again later.", ephemeral=True)
        except Exception as e:
            logger.error(f"Unexpected error during card lookup: {e}")
            await ctx.respond("An unexpected error occurred. Please try again later.", ephemeral=True)

    @discord.slash_command(name="deck_tips", description="Get tips for building a Yu-Gi-Oh deck.")
    async def slash_deck_tips(self, ctx: discord.ApplicationContext):
        """
        Provides tips for building a Yu-Gi-Oh deck.
        """
        logger.info(f"Deck tips command triggered by {ctx.user}")
        deck_tips = """
        **Yu-Gi-Oh Deck Building Tips**
        1. Choose a theme or archetype.
        2. Include at least 40 cards but no more than 60.
        3. Maintain a balance of monsters, spells, and traps.
        4. Use cards that synergize with your strategy.
        5. Include hand traps and board clears for flexibility.
        """
        await ctx.respond(deck_tips)

    @discord.slash_command(name="tournament_links", description="Get links to Yu-Gi-Oh tournaments and events.")
    async def slash_tournament_links(self, ctx: discord.ApplicationContext):
        """
        Provides links to popular Yu-Gi-Oh tournaments and events.
        """
        logger.info(f"Tournament links command triggered by {ctx.user}")
        tournament_links = """
        **Yu-Gi-Oh Tournaments and Events**
        - [Official Yu-Gi-Oh TCG Events](https://www.yugioh-card.com/uk/events/)
        - [DuelingBook Tournaments](https://www.duelingbook.com/tournaments)
        - [Online Yu-Gi-Oh Tournaments](https://yugioh-top-decks.com/tournaments)
        """
        await ctx.respond(tournament_links)


def setup(bot: discord.Bot, guild_id: int):
    """
    Sets up the Yu-Gi-Oh cog by adding it to the bot.
    """
    logger.debug(f"Setting up Yu-Gi-Oh cog with guild_id: {guild_id}")
    bot.add_cog(YuGiOh(bot, guild_id))
    logger.info("Yu-Gi-Oh cog has been added.")

    # Log the commands after setup
    logger.info("Registered commands after Yu-Gi-Oh cog setup:")
    for cmd in bot.application_commands:
        logger.info(
            f" - Command: {cmd.name} | Description: {cmd.description} | Guild ID(s): {cmd.guild_ids or 'Global'}"
        )
