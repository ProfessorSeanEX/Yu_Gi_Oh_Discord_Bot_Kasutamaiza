"""
Yu-Gi-Oh-specific commands for Kasutamaiza Bot.
"""

import discord
from discord.ext import commands
from discord.ext.pages import Paginator  # Pagination for multi-result handling
from loguru import logger
import requests  # Required for the card lookup command


class YuGiOh(commands.Cog):
    """
    Yu-Gi-Oh-specific commands for the bot.
    Includes tools like card lookup, deck tips, and tournament links.
    """

    # Class-level metadata
    __version__ = "1.0.2"
    __author__ = "ProfessorSeanEX"
    __description__ = "Provides Yu-Gi-Oh-specific tools and resources."

    category = "Yu-Gi-Oh"

    def __init__(self, bot, guild_id, token):
        """
        Initializes the Yu-Gi-Oh cog.
        """
        self.bot = bot
        self.guild_id = guild_id
        self.token = token

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
        logger.info(f"Card lookup triggered by {ctx.user} with query: {query}, mode: {search_mode}")

        api_url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        params = {"fname": query}

        # Adjust API parameters based on search mode
        search_modes = ["type", "archetype", "attribute", "race", "level"]
        if search_mode in search_modes:
            params[search_mode] = query

        # Add stat filters
        for key, value in {
            "atk>=": min_atk,
            "atk<=": max_atk,
            "def>=": min_def,
            "def<=": max_def,
            "level>=": min_level,
            "level<=": max_level,
        }.items():
            if value is not None:
                params[key[:-2]] = value

        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            cards = data.get("data", [])
            if not cards:
                await ctx.respond(f"No cards found matching {query} in {search_mode} mode.", ephemeral=True)
                return

            if len(cards) > 1:
                await self.handle_multi_result(ctx, cards)
                return

            # Single result
            card = cards[0]
            embed = self.generate_card_embed(card)
            await ctx.respond(embed=embed)

        except requests.RequestException as e:
            logger.error(f"Request Exception: {e}")
            await ctx.respond("❌ Failed to connect to the card database. Please try again later.", ephemeral=True)
        except KeyError:
            await ctx.respond(f"No card found matching {query} in {search_mode} mode.", ephemeral=True)
        except Exception as e:
            logger.error(f"Unexpected error during card lookup: {e}")
            await ctx.respond("❌ An unexpected error occurred. Please try again later.", ephemeral=True)

    def generate_card_embed(self, card):
        """
        Generates a detailed Discord embed for the provided card data.
        Includes all relevant information about the card.
        """
        # Basic card details
        embed = discord.Embed(
            title=card.get("name", "Unknown Card"),
            description=self.generate_card_description(card),
            color=discord.Color.blue(),
        )
        embed.add_field(name="Type", value=card.get("type", "Unknown"), inline=True)
        embed.add_field(name="Race", value=card.get("race", "Unknown"), inline=True)
        embed.add_field(name="Attribute", value=card.get("attribute", "N/A"), inline=True)

        # Add stats dynamically
        stats = {
            "ATK": "atk",
            "DEF": "def",
            "Level/Rank": "level",
            "Pendulum Scale": "scale",
            "Link Rating": "linkval",
        }
        for field, key in stats.items():
            if key in card:
                embed.add_field(name=field, value=card.get(key, "N/A"), inline=True)

        if "linkmarkers" in card:
            embed.add_field(name="Link Arrows", value=", ".join(card["linkmarkers"]), inline=True)

        # Archetype, Sets, and Prices
        if card.get("archetype"):
            embed.add_field(name="Archetype", value=card["archetype"], inline=True)

        if "card_sets" in card:
            sets = "\n".join([f"- {s['set_name']} ({s['set_code']})" for s in card["card_sets"]])
            embed.add_field(name="Card Sets", value=sets, inline=False)

        if "card_prices" in card:
            prices = card["card_prices"][0]
            price_details = "\n".join([
                f"**TCGPlayer**: ${prices.get('tcgplayer_price', 'N/A')}",
                f"**Ebay**: ${prices.get('ebay_price', 'N/A')}",
                f"**Amazon**: ${prices.get('amazon_price', 'N/A')}",
                f"**CoolStuffInc**: ${prices.get('coolstuffinc_price', 'N/A')}",
            ])
            embed.add_field(name="Prices", value=price_details, inline=False)

        # Images
        if "card_images" in card:
            embed.set_thumbnail(url=card["card_images"][0].get("image_url", ""))
            embed.set_image(url=card["card_images"][0].get("image_url_cropped", ""))

        # Card-specific information
        if "banlist_info" in card:
            banlist = card["banlist_info"]
            banlist_details = "\n".join(
                [f"**{key.capitalize()}**: {value}" for key, value in banlist.items()]
            )
            embed.add_field(name="Banlist Information", value=banlist_details, inline=False)

        # Add materials for Fusion/Synchro/XYZ/Link monsters
        if "materials" in card:
            embed.add_field(name="Materials", value=card["materials"], inline=False)

        return embed

    async def handle_multi_result(self, ctx, cards):
        """
        Handles multiple card results by providing a paginated embed.
        """
        embeds = [
            discord.Embed(
                title=card["name"],
                description="Multiple results found. Select a card.",
                color=discord.Color.blue(),
            ).set_thumbnail(url=card["card_images"][0].get("image_url", ""))
            for card in cards
        ]
        paginator = Paginator(pages=embeds)
        await paginator.respond(ctx.interaction)

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


def setup(bot: discord.Bot, guild_id: int, token: str):
    """
    Sets up the Yu-Gi-Oh cog by adding it to the bot.
    """
    logger.debug(f"Setting up Yu-Gi-Oh cog with guild_id: {guild_id}")
    bot.add_cog(YuGiOh(bot, guild_id, token))
    logger.info("Yu-Gi-Oh cog has been added.")

    logger.info("Registered commands after Yu-Gi-Oh cog setup:")
    for cmd in bot.application_commands:
        logger.info(
            f" - Command: {cmd.name} | Description: {cmd.description} | Guild ID(s): {cmd.guild_ids or 'Global'}"
        )
