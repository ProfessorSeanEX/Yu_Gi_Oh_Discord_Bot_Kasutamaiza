"""
Yu-Gi-Oh Helper Functions for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Provide advanced tools for managing and validating Yu-Gi-Oh gameplay, decks, and custom formats.

Updates:
- Integrated migrated functions from `helper.py`.
- Enhanced modularity for better performance and maintainability.
- Optimized queries for compatibility with dynamic filters.
"""

from typing import List, Dict, Optional
import random

# --- Core Card Handling ---
def parse_card_data(card: dict) -> dict:
    """
    Parses a card's data into a structured format.

    Args:
        card (dict): The raw card data.

    Returns:
        dict: Structured card data with key attributes.
    """
    return {
        "name": card.get("name", "Unknown"),
        "type": card.get("type", "Unknown"),
        "attribute": card.get("attribute", None),
        "atk": card.get("atk", None),
        "def": card.get("def", None),
        "level": card.get("level", None),
        "link": card.get("link", None),
        "pendulum_scale": card.get("pendulum_scale", None),
        "archetype": card.get("archetype", None),
        "effect": card.get("effect", ""),
        "banned_in": card.get("banned_in", []),
    }

# --- Card Search Query (Migrated from helper.py) ---
def build_card_query(query: str, search_mode: str, filters: dict) -> dict:
    """
    Build a query for searching Yu-Gi-Oh cards.

    Args:
        query (str): The search term (e.g., card name).
        search_mode (str): The mode of search (e.g., "type", "attribute").
        filters (dict): Additional filters for the query.

    Returns:
        dict: Query parameters for card search.
    """
    params = {"fname": query}
    valid_modes = ["type", "archetype", "attribute", "race", "level"]
    if search_mode in valid_modes:
        params[search_mode] = query
    for key, value in filters.items():
        if value is not None:
            params[key] = value
    return params

# --- Deck Validation ---
def validate_deck(deck: List[dict], format_name: str, region: str = "TCG") -> bool:
    """
    Validates a deck against the specified format and region.

    Args:
        deck (List[dict]): The list of cards in the deck.
        format_name (str): The format name (e.g., "Advanced", "Rush Duel").
        region (str): The region ("TCG" or "OCG").

    Returns:
        bool: True if the deck is valid, False otherwise.
    """
    card_count = len(deck)
    if format_name == "Advanced" and not (40 <= card_count <= 60):
        return False
    if format_name == "Rush Duel" and card_count != 40:
        return False

    # Validate regional bans
    for card in deck:
        if region in card.get("banned_in", []):
            return False
    return True

# --- Archetype and Synergy ---
def analyze_deck(deck: List[dict]) -> Dict[str, int]:
    """
    Analyzes a deck and provides type and archetype distributions.

    Args:
        deck (List[dict]): The list of cards in the deck.

    Returns:
        Dict[str, int]: A summary of card types and archetypes.
    """
    monsters = sum(1 for card in deck if "Monster" in card.get("type", ""))
    spells = sum(1 for card in deck if "Spell" in card.get("type", ""))
    traps = sum(1 for card in deck if "Trap" in card.get("type", ""))
    archetypes = {}
    for card in deck:
        archetype = card.get("archetype", "Generic")
        archetypes[archetype] = archetypes.get(archetype, 0) + 1

    return {
        "Total Cards": len(deck),
        "Monsters": monsters,
        "Spells": spells,
        "Traps": traps,
        "Archetype Distribution": archetypes,
    }

# --- Card Recommendations ---
def recommend_cards(deck: List[dict], archetype: str, limit: int = 5) -> List[dict]:
    """
    Recommends cards for a deck based on archetype.

    Args:
        deck (List[dict]): The current deck.
        archetype (str): The target archetype.
        limit (int): Maximum number of recommendations.

    Returns:
        List[dict]: Recommended cards.
    """
    all_cards = get_all_cards()
    recommended = [
        card for card in all_cards
        if archetype.lower() in card.get("archetype", "").lower() and card not in deck
    ]
    return random.sample(recommended, min(len(recommended), limit))

# --- Advanced Gameplay Mechanics ---
def resolve_chain(chain: List[dict]) -> List[dict]:
    """
    Resolves a chain of card effects in reverse order.

    Args:
        chain (List[dict]): The list of effects in chain order.

    Returns:
        List[dict]: The resolved effects in reverse order.
    """
    return chain[::-1]

# --- Custom Format Handling ---
def validate_custom_format(deck: List[dict], custom_rules: dict) -> bool:
    """
    Validates a deck against custom rules.

    Args:
        deck (List[dict]): The deck to validate.
        custom_rules (dict): The custom rules to enforce.

    Returns:
        bool: True if the deck is valid, False otherwise.
    """
    for rule, value in custom_rules.items():
        if rule == "max_card_count" and len(deck) > value:
            return False
        if rule == "banned_archetypes":
            if any(card.get("archetype") in value for card in deck):
                return False
    return True

async def setup(*args, **kwargs):
    pass
