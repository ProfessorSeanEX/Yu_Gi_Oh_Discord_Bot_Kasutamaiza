"""
Yu-Gi-Oh-specific commands for Kasutamaiza Bot.
- Contains commands specific to Yu-Gi-Oh gameplay and card management.

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX
- Purpose: Provide tools and resources tailored for Yu-Gi-Oh players.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

# Add the project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import modules
import discord
from discord.ext import commands
from discord.ext.pages import Paginator  # Pagination for multi-result handling
from loguru import logger
import requests  # Required for the card lookup command
from typing import Optional

# Utility imports
from utils import inject_helpers_into_namespace

# Inject all helpers into this module's global namespace
inject_helpers_into_namespace(globals())

logger = logging.getLogger(__name__)

class YuGiOh(commands.Cog):
    """
    Yu-Gi-Oh-specific commands for the bot.
    Includes tools like card lookup, deck tips, and tournament links.
    """

    # Class-level metadata
    __version__ = "1.0.0"
    __author__ = "ProfessorSeanEX"
    __description__ = "Provides Yu-Gi-Oh-specific tools and resources."
    category = "Yu-Gi-Oh"

    def __init__(self, bot, guild_id, token):
        """
        Initializes the Yu-Gi-Oh cog with guild-specific commands.
        """
        if not guild_id or not token:
            raise ValueError("guild_id and token must be provided for Yu-Gi-Oh cog initialization.")

        self.bot = bot
        self.guild_id = guild_id
        self.token = token
        self.start_time = datetime.now(timezone.utc)
        for cmd in self.__cog_commands__:
            logger.debug(f"Registering command '{cmd.name}' to cog '{self.__class__.__name__}' with category '{self.category}'.")

        # Enforce category attribute
        if not hasattr(self, "category") or not isinstance(self.category, str):
            logger.warning(f"Cog '{self.__class__.__name__}' is missing a 'category' attribute. Defaulting to 'Uncategorized'.")
            self.category = "Uncategorized"

        # Assign guild_ids to commands dynamically
        for cmd in self.__cog_commands__:
            if isinstance(cmd, discord.SlashCommand):
                cmd.guild_ids = [self.guild_id]

        # Debugging log for validation
        logger.debug(f"Initializing {self.__class__.__name__} with category: {self.category}")
        logger.debug(f"{self.__class__.__name__} cog initialized with guild_id={self.guild_id}.")

    async def calculate_uptime(self):
        """
        Calculates the bot's uptime since initialization.

        Returns:
            str: Formatted uptime string.
        """
        uptime = datetime.now(timezone.utc) - self.start_time
        return str(uptime).split(".")[0]

    @discord.slash_command(name="dueling", description="Get a link to DuelingBook for online dueling.")
    async def slash_dueling(self, ctx: discord.ApplicationContext):
        """
        Provides a link to DuelingBook for online dueling.
        """
        log_command(ctx, "slash_dueling")
        dueling_link = "https://www.duelingbook.com/"
        fields = {"DuelingBook": dueling_link}
        await format_embed_response(ctx, title="Ready to Duel?", fields=fields)

    @discord.slash_command(
        name="card_lookup",
        description="Search for a Yu-Gi-Oh! card by name, type, archetype, or filters."
    )
    async def slash_card_lookup(
        self,
        ctx: discord.ApplicationContext,
        query: str,
        search_mode: str = "name",
        min_atk: int = None,
        max_atk: int = None,
        min_def: int = None,
        max_def: int = None,
        min_level: int = None,
        max_level: int = None,
    ):
        """
        Fetches card information from the YGOPRODeck API based on user input.
        Supports searching by name, type, archetype, attribute, race, and level.
        """
        log_command(ctx, "slash_card_lookup")

        # Check bot permissions
        permissions = validate_permissions(ctx, ["send_messages"])
        if not permissions["has_all"]:
            await ctx.respond("Insufficient permissions to send messages.", ephemeral=True)
            return

        api_url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        filters = {
            "atk>=": min_atk,
            "atk<=": max_atk,
            "def>=": min_def,
            "def<=": max_def,
            "level>=": min_level,
            "level<=": max_level,
        }
        params = build_card_query(query=query, search_mode=search_mode, filters=filters)

        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            cards = data.get("data", [])
            if not cards:
                await format_embed_response(ctx, title="No Cards Found", fields={"Query": query}, ephemeral=True)
                return

            if len(cards) > 1:
                await self.handle_multi_result(ctx, cards)
                return

            # Single result
            card = cards[0]
            embed = generate_card_embed(card)
            await ctx.respond(embed=embed)

        except requests.RequestException as e:
            log_error("slash_card_lookup", e)
            await format_embed_response(ctx, title="Error", fields={"Message": "Failed to connect to the card database."}, color=discord.Color.red(), ephemeral=True)
        except KeyError:
            await format_embed_response(ctx, title="No Card Found", fields={"Query": query}, ephemeral=True)
        except Exception as e:
            log_error("slash_card_lookup", e)
            await format_embed_response(ctx, title="Unexpected Error", fields={"Error": str(e)}, color=discord.Color.red(), ephemeral=True)

    async def handle_multi_result(self, ctx, cards):
        """
        Handles multiple card results by providing a paginated embed.
        """
        embeds = [
            discord.Embed(title=card["name"], description="Multiple results found.")
            .set_thumbnail(url=card["card_images"][0].get("image_url", ""))
            for card in cards
        ]
        paginator = Paginator(pages=embeds)
        await paginator.respond(ctx.interaction)

    @discord.slash_command(name="deck_tips", description="Get tips for building a Yu-Gi-Oh deck.")
    async def slash_deck_tips(self, ctx: discord.ApplicationContext):
        """
        Provides tips for building a Yu-Gi-Oh deck.
        """
        log_command(ctx, "slash_deck_tips")
        deck_tips = {
            "1": "Choose a theme or archetype.",
            "2": "Include at least 40 cards but no more than 60.",
            "3": "Maintain a balance of monsters, spells, and traps.",
            "4": "Use cards that synergize with your strategy.",
            "5": "Include hand traps and board clears for flexibility."
        }
        await format_embed_response(ctx, title="Yu-Gi-Oh Deck Building Tips", fields=deck_tips)

    @discord.slash_command(name="tournament_links", description="Get links to Yu-Gi-Oh tournaments and events.")
    async def slash_tournament_links(self, ctx: discord.ApplicationContext):
        """
        Provides links to popular Yu-Gi-Oh tournaments and events.
        """
        log_command(ctx, "slash_tournament_links")
        tournament_links = {
            "Official Yu-Gi-Oh TCG Events": "https://www.yugioh-card.com/uk/events/",
            "DuelingBook Tournaments": "https://www.duelingbook.com/tournaments",
            "Online Yu-Gi-Oh Tournaments": "https://yugioh-top-decks.com/tournaments"
        }
        await format_embed_response(ctx, title="Yu-Gi-Oh Tournaments and Events", fields=tournament_links)


async def setup(bot: discord.Bot, guild_id: Optional[int] = None, token: Optional[str] = None):
    """
    Sets up the Yu-Gi-Oh cog by adding it to the bot.
    """
    logger.debug("Initializing Yu-Gi-Oh cog setup...")

    # Fetch environment variables if not explicitly provided
    guild_id = guild_id or int(os.getenv("GUILD_ID", 0))
    token = token or os.getenv("BOT_TOKEN", "")

    # Validate environment variables
    if guild_id == 0 or not token:
        logger.error("GUILD_ID or BOT_TOKEN environment variable is not set or invalid.")
        return

    try:
        # Add cog to the bot
        cog = YuGiOh(bot, guild_id, token)
        bot.add_cog(cog)
        logger.info(f"Yu-Gi-Oh cog successfully loaded for guild {guild_id}.")
        logger.info(f"Metadata: Version={YuGiOh.__version__}, Author={YuGiOh.__author__}")

        # Do not call sync_commands here; defer to on_ready
        logger.debug("Skipping sync_commands during setup. Will be handled in on_ready.")
    except Exception as e:
        logger.error(f"Failed to setup Yu-Gi-Oh cog: {e}")

        # Log registered commands after setup
        if bot.application_commands:
            logger.info("Registered commands after Yu-Gi-Oh cog setup:")
            for cmd in bot.application_commands:
                logger.info(f" - Command: {cmd.name} | Description: {cmd.description} | Guild ID(s): {cmd.guild_ids or 'Global'}")
        else:
            logger.warning("No commands found in bot.application_commands after cog setup.")
