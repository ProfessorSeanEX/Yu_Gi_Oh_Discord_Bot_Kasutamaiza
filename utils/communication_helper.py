"""
Communication Helper for Kasutamaiza Bot.
- Provides utilities for consistent communication via Discord messages and embeds.

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX
- Purpose: Provide utilities for consistent communication via Discord messages and embeds.

Notes:
- Version reset to v1.0.0 as per project phase requirements.
"""

# --- Standard Library Imports ---
# Importing necessary modules for type hints, logging, and debugging.
from typing import Optional, List, Dict
import logging

# --- Third-Party Library Imports ---
# Importing Discord-specific modules and logging utilities.
import discord
from loguru import logger

# --- Metadata for the file ---
# Metadata defines version, author, and purpose for easy tracking and debugging.
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Provide utilities for consistent communication via Discord messages and embeds."

# Initialize a logger specifically for this helper module.
# This ensures logs from helpers are easy to identify in debugging.
logger = logging.getLogger("communication_helper")

# --- Core Messaging Utilities ---
async def send_message(
    channel: discord.abc.Messageable, 
    content: Optional[str] = None, 
    embed: Optional[discord.Embed] = None
):
    """
    Sends a message to a channel or user.

    Args:
        channel (discord.abc.Messageable): The channel or user to send the message to.
        content (Optional[str]): The plain text content of the message.
        embed (Optional[discord.Embed]): An optional embed to include.

    Returns:
        discord.Message: The sent message.

    Raises:
        ValueError: If neither content nor embed is provided.
        Exception: If sending the message fails.
    """
    try:
        # Ensure either content or embed is provided.
        if content is None and embed is None:
            raise ValueError("Either content or embed must be provided.")

        # Send the message and log success.
        message = await channel.send(content=content, embed=embed)
        logger.info(f"Message sent to channel {channel.id} ({getattr(channel, 'name', 'DM')}): {content or embed.title}")
        return message
    except Exception as e:
        # Log the error with details about the target channel.
        logger.error(f"Failed to send message to channel {getattr(channel, 'id', 'Unknown')}: {e}")
        raise

async def send_dm(user: discord.User, content: Optional[str] = None, embed: Optional[discord.Embed] = None):
    """
    Sends a direct message to a user.

    Args:
        user (discord.User): The user to DM.
        content (Optional[str]): The plain text content of the message.
        embed (Optional[discord.Embed]): An optional embed to include.

    Returns:
        discord.Message: The sent message.

    Raises:
        ValueError: If neither content nor embed is provided.
        Exception: If sending the DM fails.
    """
    try:
        # Ensure either content or embed is provided.
        if content is None and embed is None:
            raise ValueError("Either content or embed must be provided.")

        # Create a DM channel and send the message.
        dm_channel = await user.create_dm()
        message = await dm_channel.send(content=content, embed=embed)
        logger.info(f"DM sent to user {user.name} (ID: {user.id}): {content or embed.title}")
        return message
    except Exception as e:
        # Log the error with details about the user.
        logger.error(f"Failed to send DM to user {user.name} (ID: {user.id}): {e}")
        raise

# --- Broadcast Utilities ---
async def broadcast_message(
    bot: discord.Bot, 
    channel_ids: List[int], 
    content: Optional[str] = None, 
    embed: Optional[discord.Embed] = None
):
    """
    Broadcasts a message to multiple channels.

    Args:
        bot (discord.Bot): The bot instance.
        channel_ids (List[int]): List of channel IDs to broadcast to.
        content (Optional[str]): The plain text content of the message.
        embed (Optional[discord.Embed]): An optional embed to include.

    Returns:
        None

    Example:
        await broadcast_message(bot, [1234567890, 987654321], content="Hello, everyone!")
    """
    for channel_id in channel_ids:
        try:
            # Fetch the channel by its ID.
            channel = bot.get_channel(channel_id)
            
            if channel:
                # Send the message to the channel if it exists.
                await send_message(channel, content=content, embed=embed)
                logger.info(f"Broadcast message sent to channel {channel.id} ({channel.name}).")
            else:
                # Log a warning if the channel could not be found.
                logger.warning(f"Channel ID {channel_id} not found. Skipping broadcast.")
        except Exception as e:
            # Log an error if the broadcast to the channel fails.
            logger.error(f"Failed to broadcast to channel {channel_id}: {e}")

# --- Template and Alert Utilities ---
def create_embed(
    title: str, 
    description: str, 
    fields: Optional[Dict[str, str]] = None, 
    color=discord.Color.blue()
) -> discord.Embed:
    """
    Creates a templated embed for messaging.

    Args:
        title (str): The embed title.
        description (str): The embed description.
        fields (Optional[Dict[str, str]]): A dictionary of fields to add to the embed.
        color (discord.Color, optional): The embed color. Defaults to blue.

    Returns:
        discord.Embed: The created embed.

    Example:
        create_embed(title="Info", description="This is an info message.", fields={"Field1": "Value1"})
    """
    # Create an embed object with the provided title, description, and color.
    embed = discord.Embed(title=title, description=description, color=color)
    
    # Add fields to the embed if provided.
    if fields:
        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=False)
    
    # Log the creation of the embed for debugging.
    logger.debug(f"Embed created: {title}")
    return embed

async def send_alert(
    bot: discord.Bot, 
    channel_id: int, 
    alert_type: str, 
    content: Optional[str] = None
):
    """
    Sends an alert message to a specific channel.

    Args:
        bot (discord.Bot): The bot instance.
        channel_id (int): The ID of the channel to send the alert to.
        alert_type (str): The type of alert (e.g., "Critical", "Info").
        content (Optional[str]): The alert message content.

    Returns:
        discord.Message: The sent message.

    Example:
        await send_alert(bot, 1234567890, alert_type="Critical", content="This is a critical alert!")
    """
    # Fetch the channel by its ID.
    channel = bot.get_channel(channel_id)
    
    if channel:
        try:
            # Create an embed based on the alert type.
            embed = create_embed(
                title=f"{alert_type.capitalize()} Alert",
                description=content or "An alert has been triggered.",
                color=discord.Color.red() if alert_type.lower() == "critical" else discord.Color.yellow()
            )
            # Send the alert embed to the channel.
            await send_message(channel, embed=embed)
            logger.info(f"{alert_type.capitalize()} alert sent to channel {channel.id} ({channel.name}).")
        except Exception as e:
            # Log an error if the alert fails.
            logger.error(f"Failed to send {alert_type.lower()} alert to channel {channel_id}: {e}")
    else:
        # Log a warning if the channel could not be found.
        logger.warning(f"Channel ID {channel_id} not found for alert. Skipping alert.")

# --- Interaction Handling Utilities ---
async def respond_to_mention(message: discord.Message, response: str):
    """
    Responds to a bot mention with a specific message.

    Args:
        message (discord.Message): The message mentioning the bot.
        response (str): The response content.

    Returns:
        discord.Message: The sent response message.
    """
    try:
        if message.mentions and message.guild.me in message.mentions:
            reply = await message.reply(content=response)
            logger.info(f"Responded to mention in channel {message.channel.id} ({message.channel.name}).")
            return reply
    except Exception as e:
        logger.error(f"Failed to respond to mention in channel {message.channel.id if hasattr(message.channel, 'id') else 'Unknown'}: {e}")
        raise

# --- Response Utilities ---
def respond_with_error(ctx, title: str, description: str) -> None:
    """
    Sends an embed response for unexpected errors.

    Args:
        ctx: The command context.
        title (str): The title of the error message.
        description (str): The description of the error.

    Returns:
        None

    Example:
        respond_with_error(ctx, "Error Occurred", "Unable to process your request.")
    """
    try:
        # Log the error being reported.
        logger.warning(f"Sending error response in context {ctx.channel.name if hasattr(ctx, 'channel') else 'Unknown'}: {title}")
        
        # Use a helper function to format and send the error embed.
        return format_embed_response(
            ctx,
            title=title,
            fields={"Details": description},  # Include details of the error in the embed fields.
            color=discord.Color.red(),  # Use red color for error messages.
            ephemeral=True  # Make the response ephemeral so only the user sees it.
        )
    except Exception as e:
        # Log any failures that occur while sending the error response.
        logger.error(f"Failed to send error response: {e}")

def respond_with_embed(
    ctx,
    title: str,
    description: str = None,
    fields: dict = None,
    color: discord.Color = discord.Color.default(),
    ephemeral: bool = False
) -> None:
    """
    Sends an embed response with optional fields and description.

    Args:
        ctx: The context of the command.
        title (str): The title of the embed.
        description (str, optional): The description of the embed.
        fields (dict, optional): The fields for the embed.
        color (discord.Color, optional): The color of the embed.
        ephemeral (bool, optional): Whether the response should be ephemeral.

    Returns:
        None

    Updates:
        - Integrated inline pagination handling for field overflow.
        - Removed dependency on external helpers like paginate_embed_fields.
    """
    try:
        # Function to split fields if they exceed character limits
        def split_fields(input_fields, max_length=1024):
            split_result = {}
            for field_name, field_value in input_fields.items():
                if len(field_value) > max_length:
                    chunks = [
                        field_value[i:i + max_length]
                        for i in range(0, len(field_value), max_length)
                    ]
                    for idx, chunk in enumerate(chunks, start=1):
                        split_result[f"{field_name} (Part {idx})"] = chunk
                else:
                    split_result[field_name] = field_value
            return split_result

        # Handle field splitting
        if fields:
            fields = split_fields(fields)

        # Determine if multiple embeds are required
        if fields and len(fields) > 25:
            embeds = []
            chunk_size = 25
            field_chunks = [
                dict(list(fields.items())[i:i + chunk_size])
                for i in range(0, len(fields), chunk_size)
            ]
            for i, chunk in enumerate(field_chunks):
                embed = discord.Embed(
                    title=f"{title} (Page {i + 1}/{len(field_chunks)})",
                    color=color
                )
                for key, value in chunk.items():
                    embed.add_field(name=key, value=value, inline=False)
                embeds.append(embed)

            # Paginate the embeds
            paginator = Paginator(pages=embeds)
            return paginator.respond(ctx.interaction)

        # Single embed case
        embed = discord.Embed(title=title, description=description, color=color)
        if fields:
            for key, value in fields.items():
                embed.add_field(name=key, value=value, inline=False)

        # Log the action
        logger.info(f"Responding with embed: {title}")

        # Send the response
        return ctx.respond(embed=embed, ephemeral=ephemeral)
    except Exception as e:
        logger.error(f"Error in respond_with_embed: {e}")

async def format_embed_response(
    ctx, 
    title: str, 
    fields: dict, 
    color: discord.Color = discord.Color.blue(), 
    ephemeral: bool = False
) -> None:
    """
    Formats and sends an embedded response. Uses split_embed_fields to handle long fields.

    Args:
        ctx (discord.ApplicationContext): The context of the command.
        title (str): The title of the embed.
        fields (dict): A dictionary of fields to include in the embed.
        color (discord.Color, optional): The embed color. Defaults to blue.
        ephemeral (bool, optional): Whether the response is ephemeral. Defaults to False.

    Returns:
        None

    Example:
        await format_embed_response(ctx, "Results", fields={"Field1": "Value1"})
    """
    try:
        # Process any fields that exceed Discord's character limits.
        fields = split_embed_fields(fields)

        # Create the embed object with the specified title and color.
        embed = discord.Embed(title=title, description="", color=color)

        # Add the processed fields to the embed.
        for field_name, field_value in fields.items():
            embed.add_field(name=field_name, value=field_value, inline=False)

        # Log the creation of the formatted embed for debugging.
        logger.debug(f"Formatted embed created: {title}")
        
        # Send the response using the context.
        await ctx.respond(embed=embed, ephemeral=ephemeral)
    except Exception as e:
        # Log any failures that occur while formatting or sending the response.
        logger.error(f"Failed to format embed response: {e}")

# --- Utility Functions ---
def split_embed_fields(fields: dict) -> dict:
    """
    Splits embed fields that exceed Discord's 1024-character limit.

    Args:
        fields (dict): A dictionary of embed fields to process.

    Returns:
        dict: Processed fields with long values split into multiple parts.

    Example:
        split_embed_fields({"Field1": "A very long text..."})
        # Output:
        # {"Field1 (Part 1)": "First 1024 characters...", "Field1 (Part 2)": "Next 1024 characters..."}
    """
    # Initialize a dictionary to store processed fields.
    processed_fields = {}
    
    for field_name, field_value in fields.items():
        # If the field value exceeds 1024 characters, split it into chunks.
        if len(field_value) > 1024:
            split_values = [field_value[i:i + 1024] for i in range(0, len(field_value), 1024)]
            for idx, chunk in enumerate(split_values, start=1):
                # Add each chunk to the processed fields with a part identifier.
                processed_fields[f"{field_name} (Part {idx})"] = chunk
        else:
            # If the field value is within the limit, keep it as is.
            processed_fields[field_name] = field_value
    
    # Log the processed fields for debugging.
    logger.debug(f"Processed embed fields: {processed_fields.keys()}")
    return processed_fields

def organize_embed_fields(fields: Dict[str, List[str]], max_length: int = 1024) -> Dict[str, List[str]]:
    """
    Organizes and splits embed fields to fit Discord's character limits.

    Args:
        fields (Dict[str, List[str]]): Dictionary of field titles and their respective content lists.
        max_length (int): Maximum character length for Discord embed fields.

    Returns:
        Dict[str, List[str]]: Updated dictionary with split content.

    Example:
        organize_embed_fields({"Title": ["Item1", "Item2", ...]})
        # Output:
        # {"Title (Part 1)": ["First 1024 characters..."], "Title (Part 2)": ["Next 1024 characters..."]}
    """
    # Initialize a dictionary to store organized fields.
    organized_fields = {}
    
    for title, content_list in fields.items():
        # Combine all content into a single string.
        concatenated_content = "\n".join(content_list)
        
        if len(concatenated_content) <= max_length:
            # If the content fits within the limit, add it as is.
            organized_fields[title] = [concatenated_content]
        else:
            # Split the content into chunks of max_length.
            chunks = [concatenated_content[i:i + max_length] for i in range(0, len(concatenated_content), max_length)]
            for idx, chunk in enumerate(chunks, start=1):
                # Add each chunk with a part identifier.
                organized_fields[f"{title} (Part {idx})"] = [chunk]
    
    # Log the organized fields for debugging.
    logger.debug(f"Organized embed fields: {organized_fields.keys()}")
    return organized_fields

def generate_card_embed(card: dict) -> discord.Embed:
    """
    Generates a Discord embed object for a Yu-Gi-Oh! card.

    Args:
        card (dict): Card data from the YGOPRODeck API.

    Returns:
        discord.Embed: Embed object representing the card.

    Example:
        generate_card_embed(card_data)
    """
    try:
        # Create an embed with the card's details.
        embed = discord.Embed(
            title=card.get("name", "Unknown Card"),
            description=card.get("desc", "No description available."),
            color=discord.Color.blue()
        )
        # Set the thumbnail image for the card, if available.
        embed.set_thumbnail(url=card.get("card_images", [{}])[0].get("image_url", ""))
        
        # Add fields for card attributes.
        embed.add_field(name="Type", value=card.get("type", "N/A"), inline=True)
        embed.add_field(name="Attribute", value=card.get("attribute", "N/A"), inline=True)
        embed.add_field(name="Level", value=str(card.get("level", "N/A")), inline=True)
        embed.add_field(name="ATK", value=str(card.get("atk", "N/A")), inline=True)
        embed.add_field(name="DEF", value=str(card.get("def", "N/A")), inline=True)
        
        # Log successful embed generation.
        logger.info(f"Card embed generated for: {card.get('name', 'Unknown Card')}")
        return embed
    except Exception as e:
        # Log any errors that occur during embed generation.
        logger.error(f"Failed to generate card embed: {e}")
        raise

def stringify_fields(fields: dict) -> dict:
    """
    Ensures all values in the fields dictionary are strings.

    Args:
        fields (dict): A dictionary of fields.

    Returns:
        dict: A dictionary with all values converted to strings.

    Example:
        stringify_fields({"Field1": 123, "Field2": ["Item1", "Item2"]})
        # Output:
        # {"Field1": "123", "Field2": "['Item1', 'Item2']"}
    """
    try:
        # Convert all field values to strings.
        converted_fields = {key: str(value) for key, value in fields.items()}
        
        # Log the conversion process.
        logger.debug(f"Stringified fields: {converted_fields.keys()}")
        return converted_fields
    except Exception as e:
        # Log any errors that occur during the conversion process.
        logger.error(f"Error in stringify_fields: {e}")
        return {}

# --- Setup Function ---
async def setup(*args, **kwargs):
    """
    Setup function for initializing the Communication Helper module.

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
        # Log the start of the setup process for debugging purposes.
        logger.info("Setting up Communication Helper module...")
        
        # Log successful setup completion along with the module's metadata.
        logger.info(f"Communication Helper module setup completed successfully. Metadata: Version={__version__}, Author={__author__}")
    except Exception as e:
        # Log any errors encountered during setup to assist in debugging.
        logger.error(f"Error during Communication Helper setup: {e}")
        raise
