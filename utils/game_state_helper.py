"""
Game State Tracking Helper for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Manage and track the dynamic state of the game, including field setup, turns, and player stats.

Updates:
- Added `GameState` class for structured game state management.
- Enhanced utilities for turn and phase progression.
- Improved field management with robust card placement and removal logic.
- Integrated life point tracking for players.
"""

from typing import List, Dict, Optional
import copy
from loguru import logger

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Facilitate game state tracking, turn management, and field validation."

# --- Core Game State Structure ---
class GameState:
    """
    Represents the state of a Yu-Gi-Oh game.
    """

    def __init__(self, players: List[str]):
        """
        Initializes the game state with player information.

        Args:
            players (List[str]): List of player IDs.
        """
        self.players = players
        self.current_turn = 0
        self.current_phase = "Draw Phase"
        self.field_state = {player: self.initialize_field() for player in players}
        self.graveyards = {player: [] for player in players}
        self.banished = {player: [] for player in players}
        self.life_points = {player: 8000 for player in players}
        self.logs = []

        logger.info("Game state initialized.")

    def initialize_field(self) -> Dict[str, List[Optional[dict]]]:
        """
        Initializes an empty field state for a player.

        Returns:
            Dict[str, List[Optional[dict]]]: Field structure with empty zones.
        """
        return {
            "monster_zones": [None] * 5,
            "spell_trap_zones": [None] * 5,
            "field_zone": None,
            "extra_deck": [],
            "deck": [],
            "hand": [],
        }

# --- Game State Utilities ---
def save_game_state(game_state: GameState) -> dict:
    """
    Saves the current game state as a dictionary.

    Args:
        game_state (GameState): The current game state.

    Returns:
        dict: A serialized game state.
    """
    return copy.deepcopy(game_state.__dict__)

def load_game_state(saved_state: dict) -> GameState:
    """
    Restores a game state from a serialized dictionary.

    Args:
        saved_state (dict): The serialized game state.

    Returns:
        GameState: The restored game state.
    """
    game_state = GameState(players=saved_state["players"])
    game_state.__dict__.update(saved_state)
    logger.info("Game state loaded.")
    return game_state

# --- Turn and Phase Management ---
def next_phase(game_state: GameState):
    """
    Advances the game to the next phase.

    Args:
        game_state (GameState): The current game state.

    Returns:
        None
    """
    phases = [
        "Draw Phase", "Standby Phase", "Main Phase 1", "Battle Phase",
        "Main Phase 2", "End Phase"
    ]
    current_index = phases.index(game_state.current_phase)
    game_state.current_phase = phases[(current_index + 1) % len(phases)]
    if game_state.current_phase == "Draw Phase":
        game_state.current_turn += 1
        logger.info(f"Turn {game_state.current_turn} started.")
    logger.info(f"Phase advanced to {game_state.current_phase}.")

def get_current_turn(game_state: GameState) -> int:
    """
    Retrieves the current turn number.

    Args:
        game_state (GameState): The current game state.

    Returns:
        int: Current turn number.
    """
    return game_state.current_turn

# --- Field Management ---
def place_card_on_field(player: str, zone: str, card: dict, game_state: GameState) -> bool:
    """
    Places a card in the specified zone on the field.

    Args:
        player (str): The player ID.
        zone (str): The zone to place the card in.
        card (dict): The card to place.
        game_state (GameState): The current game state.

    Returns:
        bool: True if the card was placed successfully, False otherwise.
    """
    if zone not in game_state.field_state[player]:
        logger.warning(f"Invalid zone {zone} for player {player}.")
        return False

    if isinstance(game_state.field_state[player][zone], list):
        for i in range(len(game_state.field_state[player][zone])):
            if game_state.field_state[player][zone][i] is None:
                game_state.field_state[player][zone][i] = card
                logger.info(f"Card placed in {zone} for player {player}.")
                return True
        logger.warning(f"No available space in {zone} for player {player}.")
        return False

    if game_state.field_state[player][zone] is None:
        game_state.field_state[player][zone] = card
        logger.info(f"Card placed in {zone} for player {player}.")
        return True

    logger.warning(f"Zone {zone} is already occupied for player {player}.")
    return False

def remove_card_from_field(player: str, zone: str, index: Optional[int], game_state: GameState) -> Optional[dict]:
    """
    Removes a card from the specified zone on the field.

    Args:
        player (str): The player ID.
        zone (str): The zone to remove the card from.
        index (Optional[int]): Index within the zone, if applicable.
        game_state (GameState): The current game state.

    Returns:
        Optional[dict]: The removed card, or None if the zone was empty.
    """
    if zone not in game_state.field_state[player]:
        logger.warning(f"Invalid zone {zone} for player {player}.")
        return None

    if isinstance(game_state.field_state[player][zone], list) and index is not None:
        card = game_state.field_state[player][zone][index]
        game_state.field_state[player][zone][index] = None
        logger.info(f"Card removed from {zone} at index {index} for player {player}.")
        return card

    card = game_state.field_state[player][zone]
    game_state.field_state[player][zone] = None
    logger.info(f"Card removed from {zone} for player {player}.")
    return card

# --- Player Life Points ---
def adjust_life_points(player: str, amount: int, game_state: GameState):
    """
    Adjusts a player's life points by a specified amount.

    Args:
        player (str): The player ID.
        amount (int): The amount to adjust life points by.
        game_state (GameState): The current game state.

    Returns:
        None
    """
    game_state.life_points[player] += amount
    logger.info(f"Player {player} life points adjusted by {amount}. New total: {game_state.life_points[player]}.")

def get_life_points(player: str, game_state: GameState) -> int:
    """
    Retrieves a player's current life points.

    Args:
        player (str): The player ID.
        game_state (GameState): The current game state.

    Returns:
        int: Player's current life points.
    """
    return game_state.life_points[player]

async def setup(*args, **kwargs):
    pass
