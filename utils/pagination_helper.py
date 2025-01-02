"""
Pagination Helper Functions for Kasutamaiza Bot.
- Provides utilities for managing paginated content.

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX
- Purpose: Manage paginated content for multi-result commands.

Notes:
- Version reset to v1.0.0 as per project phase requirements.
"""

# --- Standard Library Imports ---
# Importing necessary modules for type hints and logging.
from typing import List, Dict
import logging

# --- Third-Party Library Imports ---
# Importing Discord-specific modules for embeds and pagination.
import discord
from discord.ext.pages import Paginator

# --- Metadata for the file ---
# Metadata defines version, author, and purpose for easy tracking and debugging.
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Provide utilities for managing paginated content."

# Initialize a logger specifically for this helper module.
# This ensures logs from helpers are easy to identify in debugging.
logger = logging.getLogger("pagination_helper")

# --- Generic Pagination Functions ---
async def handle_multi_result(ctx, items: List[Dict], title_key: str, desc_key: str, img_key: str):
    """
    Handles multiple results by providing a paginated embed.

    Args:
        ctx: The command context.
        items (List[Dict]): List of item data.
        title_key (str): Key to extract the title from item data.
        desc_key (str): Key to extract the description from item data.
        img_key (str): Key to extract the image URL from item data.

    Returns:
        None

    Example:
        await handle_multi_result(ctx, items, title_key="name", desc_key="description", img_key="image_url")
    """
    try:
        # Ensure the items list is not empty.
        if not items:
            logger.warning("No items provided for pagination.")
            await ctx.respond("No results found.", ephemeral=True)
            return

        # Generate embeds for each item based on the provided keys.
        embeds = [
            discord.Embed(title=item.get(title_key, "Untitled"))
            .set_description(item.get(desc_key, "No description available."))
            .set_thumbnail(url=item.get(img_key, ""))
            for item in items
        ]

        # Initialize and start the paginator.
        paginator = Paginator(pages=embeds)
        await paginator.respond(ctx.interaction)
        logger.info("Pagination completed successfully.")
    except Exception as e:
        # Log any errors during the pagination process.
        logger.error(f"Error in handle_multi_result: {e}")
        await ctx.respond("An error occurred while handling pagination.", ephemeral=True)

def paginate_embed_fields(fields: dict, limit: int = 1024) -> list[dict]:
    """
    Splits embed fields into chunks suitable for pagination.

    Args:
        fields (dict): A dictionary of embed fields to paginate.
        limit (int): Character limit per field. Defaults to 1024.

    Returns:
        list[dict]: A list of paginated field dictionaries.

    Example:
        fields = {"Field1": "Value1", "Field2": "Value2"}
        paginate_embed_fields(fields, limit=1024)

    Category:
        Pagination Helper
    """
    logger.debug("Splitting embed fields for pagination with limit: %d characters.", limit)
    paginated_fields = []

    # Iterate over each field and split values exceeding the limit.
    for name, value in fields.items():
        if len(value) > limit:
            chunks = [value[i:i + limit] for i in range(0, len(value), limit)]
            for idx, chunk in enumerate(chunks, start=1):
                paginated_fields.append({f"{name} (Part {idx})": chunk})
        else:
            paginated_fields.append({name: value})

    logger.info("Successfully split embed fields into %d paginated chunks.", len(paginated_fields))
    return paginated_fields

def paginate_dict(data: dict, limit: int = 1024) -> list[dict]:
    """
    Paginates a dictionary into chunks suitable for embed fields.

    Args:
        data (dict): The dictionary to paginate.
        limit (int, optional): Character limit for each chunk. Defaults to 1024.

    Returns:
        list[dict]: List of dictionaries, each containing a chunk of key-value pairs.

    Example:
        chunks = paginate_dict({"Key1": "Value1", "Key2": "Value2"}, limit=1024)
    """
    # Initialize variables for pagination.
    chunks = []
    current_chunk = {}
    current_length = 0

    # Iterate through dictionary items and split into chunks.
    for key, value in data.items():
        entry = f"{key}: {value}"  # Format as "Key: Value".
        if current_length + len(entry) > limit:
            chunks.append(current_chunk)  # Save the current chunk.
            current_chunk = {}  # Start a new chunk.
            current_length = 0  # Reset the length counter.
        current_chunk[key] = value  # Add entry to the current chunk.
        current_length += len(entry)  # Update the length counter.

    # Append the final chunk if not empty.
    if current_chunk:
        chunks.append(current_chunk)

    # Log the pagination process for debugging.
    logger.debug(f"Paginated dictionary into {len(chunks)} chunks.")
    return chunks

def paginate_embeds(title: str, fields: dict, color=discord.Color.blue()) -> list[discord.Embed]:
    """
    Generates paginated embeds for fields exceeding Discord's limits.

    Args:
        title (str): The title for the embeds.
        fields (dict): A dictionary of fields to paginate.
        color (discord.Color, optional): Embed color. Defaults to blue.

    Returns:
        list[discord.Embed]: List of paginated embeds.

    Example:
        fields = {"Field1": "Value1", "Field2": "Value2"}
        paginate_embeds("Paginated Embed", fields)

    Category:
        Pagination Helper
    """
    logger.debug("Creating paginated embeds for title: '%s'.", title)
    embeds = []

    # Paginate fields using helper function.
    field_chunks = paginate_embed_fields(fields)
    for idx, chunk in enumerate(field_chunks, start=1):
        embed = discord.Embed(
            title=f"{title} (Page {idx}/{len(field_chunks)})",
            color=color
        )
        for field in chunk:
            for name, value in field.items():
                embed.add_field(name=name, value=value, inline=False)

        # Add each constructed embed to the list.
        embeds.append(embed)

    logger.info("Generated %d paginated embeds successfully for title: '%s'.", len(embeds), title)
    return embeds

# --- Specific Pagination Functions ---
async def paginate_cards(ctx, cards: List[Dict]):
    """
    Handles multiple card results with pagination, preserving the card-specific logic.

    Args:
        ctx: The command context.
        cards (List[Dict]): List of card data.

    Returns:
        None

    Example:
        await paginate_cards(ctx, card_data)
    """
    try:
        # Ensure the card list is not empty.
        if not cards:
            logger.warning("No card results to paginate.")
            await ctx.respond("No card results found.", ephemeral=True)
            return

        # Generate embeds for each card with specific details.
        embeds = [
            discord.Embed(
                title=card.get("name", "Unknown Card"),
                description=card.get("desc", "No description available.")
            ).set_thumbnail(url=card.get("card_images", [{}])[0].get("image_url", ""))
            for card in cards
        ]

        # Initialize and start the paginator.
        paginator = Paginator(pages=embeds)
        await paginator.respond(ctx.interaction)
        logger.info("Card pagination completed successfully.")
    except Exception as e:
        # Log any errors during the card pagination process.
        logger.error(f"Error in paginate_cards: {e}")
        await ctx.respond("An error occurred while paginating cards.", ephemeral=True)

async def paginate_text(ctx, text: str, title: str = "Paginated Text", limit: int = 2000):
    """
    Handles pagination for long text data.

    Args:
        ctx: The command context.
        text (str): The large text to paginate.
        title (str): Title for each page.
        limit (int): Character limit for each page. Default is 2000.

    Returns:
        None

    Example:
        await paginate_text(ctx, long_text, title="My Paginated Text")

    Category:
        Pagination Helper
    """
    try:
        logger.debug("Starting text pagination for title: '%s'.", title)

        # Ensure the text is not empty.
        if not text:
            logger.warning("No text provided for pagination.")
            await ctx.respond("No content to display.", ephemeral=True)
            return

        # Split the text into chunks based on the character limit.
        text_chunks = [text[i:i + limit] for i in range(0, len(text), limit)]

        # Generate embeds for each text chunk.
        pages = [
            discord.Embed(
                title=f"{title} (Page {i + 1}/{len(text_chunks)})",
                description=chunk
            )
            for i, chunk in enumerate(text_chunks)
        ]

        # Initialize and start the paginator.
        paginator = Paginator(pages=pages)
        await paginator.respond(ctx.interaction)
        logger.info("Text pagination completed successfully for title: '%s'.", title)
    except Exception as e:
        logger.error("Error in text pagination for title '%s': %s", title, e)
        await ctx.respond("An error occurred while paginating text.", ephemeral=True)

async def paginate_list(ctx, items: List[str], title: str = "Paginated List", items_per_page: int = 10):
    """
    Paginates a list of strings into multiple pages.

    Args:
        ctx: The command context.
        items (List[str]): The list of strings to paginate.
        title (str): Title for each page.
        items_per_page (int): Number of items per page.

    Returns:
        None

    Example:
        await paginate_list(ctx, my_items, title="My Items")
    """
    try:
        # Ensure the items list is not empty.
        if not items:
            logger.warning("No items provided for pagination.")
            await ctx.respond("No items to display.", ephemeral=True)
            return

        # Chunk the list into pages based on the items per page limit.
        item_chunks = [items[i:i + items_per_page] for i in range(0, len(items), items_per_page)]

        # Generate embeds for each chunk of items.
        pages = [
            discord.Embed(
                title=f"{title} (Page {i + 1}/{len(item_chunks)})",
                description="\n".join(chunk)
            )
            for i, chunk in enumerate(item_chunks)
        ]

        # Initialize and start the paginator.
        paginator = Paginator(pages=pages)
        await paginator.respond(ctx.interaction)
        logger.info("List pagination completed successfully.")
    except Exception as e:
        # Log any errors during the list pagination process.
        logger.error(f"Error in paginate_list: {e}")
        await ctx.respond("An error occurred while paginating the list.", ephemeral=True)

# --- Setup Function ---
async def setup(*args, **kwargs):
    """
    Setup function for the Pagination Helper module.

    Logs metadata and confirms setup is complete.

    Args:
        *args: Positional arguments for future compatibility.
        **kwargs: Keyword arguments for future compatibility.

    Raises:
        Exception: If setup fails.

    Example:
        await setup()
    """
    try:
        # Log the start of the setup process.
        logger.info("Setting up Pagination Helper module...")
        
        # Log successful setup completion along with the module's metadata.
        logger.info(f"Pagination Helper setup completed successfully. Metadata: Version={__version__}, Author={__author__}")
    except Exception as e:
        # Log any errors encountered during setup.
        logger.error(f"Error during Pagination Helper setup: {e}")
