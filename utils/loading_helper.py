"""
Loading Helper for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Provides centralized functions for dynamically loading modules (cogs, utilities, etc.).

Notes:
- Includes enhanced error handling and reloading capabilities.
- Categorized for clarity and maintainability.
"""

# --- Standard Library Imports ---
import asyncio  # For managing asynchronous tasks.
from pathlib import Path  # To handle file system paths.
from importlib import import_module, reload  # To dynamically load and reload modules.
from typing import List, Optional, Dict  # For type annotations.

# --- Third-Party Imports ---
from loguru import logger  # Advanced logging utility.

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Provide centralized functions for dynamically loading modules (cogs, utilities, etc.)."

# --- Core Module Loading Functions ---
async def load_modules_from_directory(
    directory: str,
    module_type: str,
    bot=None,
    guild_id: Optional[int] = None,
    token: Optional[str] = None
) -> Dict[str, list]:
    """
    Dynamically loads Python modules from a specified directory.

    Args:
        directory (str): The directory path containing module files.
        module_type (str): The type of modules (e.g., 'cogs', 'utils').
        bot (optional): The Discord bot instance, passed to setup functions.
        guild_id (Optional[int]): Guild ID for scoping specific modules.
        token (Optional[str]): Bot token, if needed for validation.

    Returns:
        Dict[str, list]: Summary of loaded and failed modules.

    Notes:
        - Skips modules without callable `setup` functions.
        - Includes detailed logging for each loaded or failed module.
    """
    loaded = []  # Tracks successfully loaded modules.
    failed = []  # Tracks modules that failed to load.

    logger.info(f"Loading {module_type} from directory: {directory}")
    try:
        path = Path(directory)  # Convert string path to a Path object.
        if not path.is_dir():  # Ensure the directory exists.
            raise ValueError(f"Invalid directory: {directory}")

        for file_name in path.iterdir():  # Iterate through files in the directory.
            if file_name.suffix == ".py" and not file_name.name.startswith("_"):  # Skip non-Python files.
                module_name = f"{module_type}.{file_name.stem}"  # Construct the module name.
                try:
                    module = import_module(module_name)  # Import the module dynamically.
                    if hasattr(module, "setup") and callable(module.setup):  # Check for a callable `setup`.
                        if asyncio.iscoroutinefunction(module.setup):  # Handle async setup functions.
                            await module.setup(bot, guild_id, token)
                        else:  # Handle synchronous setup functions.
                            module.setup(bot, guild_id, token)
                        loaded.append(module_name)  # Add to loaded modules list.
                        logger.info(f"Successfully loaded {module_type}: {module_name}")
                    else:  # Log if no valid `setup` is found.
                        logger.warning(f"Skipped {module_name}: Missing callable 'setup' function.")
                        failed.append(module_name)
                except Exception as e:  # Handle import/setup errors.
                    failed.append(module_name)
                    logger.error(f"Error loading {module_type} {module_name}: {e}")
    except Exception as e:  # Handle directory errors.
        logger.error(f"Error loading modules from {directory}: {e}")
        return {"loaded": [], "failed": [str(e)]}

    return {"loaded": loaded, "failed": failed}  # Return load summary.

def validate_module_attributes(module, required_attributes: list) -> bool:
    """
    Validates that a module contains all required attributes.

    Args:
        module: The imported module to validate.
        required_attributes (list): Attributes that must be present in the module.

    Returns:
        bool: True if all required attributes exist, False otherwise.

    Notes:
        - Logs a warning if any required attributes are missing.
    """
    missing = [attr for attr in required_attributes if not hasattr(module, attr)]  # Check for missing attributes.
    if missing:  # Log missing attributes.
        logger.warning(f"Module {module.__name__} is missing attributes: {missing}")
        return False
    return True  # Return True if all attributes are present.

def filter_modules_in_directory(directory: str) -> List[Path]:
    """
    Filters Python files in a directory, excluding private files.

    Args:
        directory (str): Path to the directory containing files.

    Returns:
        List[Path]: Filtered list of Python files.

    Notes:
        - Excludes files starting with an underscore (_).
    """
    logger.debug(f"Filtering Python files in directory: {directory}")
    path = validate_directory(directory)  # Validate the directory first.
    return [file for file in path.iterdir() if file.suffix == ".py" and not file.name.startswith("_")]

def validate_directory(directory: str) -> Path:
    """
    Validates that a directory exists and is accessible.

    Args:
        directory (str): Path to the directory to validate.

    Returns:
        Path: Validated Path object.

    Raises:
        ValueError: If the directory is invalid or inaccessible.
    """
    logger.debug(f"Validating directory: {directory}")
    path = Path(directory)
    if not path.is_dir():  # Check if it's a valid directory.
        raise ValueError(f"Invalid directory: {directory}")
    return path  # Return the validated Path object.

# --- Logging Functions ---
def log_module_status(module_name: str, status: str, error: Optional[str] = None):
    """
    Logs the status of a module during the load process.

    Args:
        module_name (str): Name of the module.
        status (str): Status of the module ('success', 'skipped', 'failed').
        error (Optional[str]): Error message, if applicable.

    Returns:
        None
    """
    if status == "success":
        logger.info(f"Successfully loaded module: {module_name}")
    elif status == "skipped":
        logger.warning(f"Skipped module: {module_name} (missing 'setup')")
    elif status == "failed":
        logger.error(f"Failed to load module: {module_name} | Error: {error}")

# --- Utility Enhancements ---
async def reload_modules_from_directory(directory: str, module_type: str) -> Dict[str, list]:
    """
    Dynamically reloads modules from a specified directory.

    Args:
        directory (str): Path to the directory containing modules.
        module_type (str): Type of modules to reload.

    Returns:
        Dict[str, list]: Summary of successfully reloaded and failed modules.
    """
    logger.info(f"Reloading {module_type} from directory: {directory}")
    try:
        results = await load_modules_from_directory(directory, module_type)  # Reuse loading logic for reloading.
        return results  # Return the reload results.
    except Exception as e:
        logger.error(f"Error reloading modules: {e}")
        return {"loaded": [], "failed": [str(e)]}

# --- Setup Block ---
async def setup(directory: str, module_type: str, bot=None, guild_id: Optional[int] = None, token: Optional[str] = None):
    """
    Initializes the Loading Helper by loading modules from a specified directory.

    Args:
        directory (str): The directory path containing module files.
        module_type (str): The type of modules to load (e.g., 'cogs', 'utils').
        bot (optional): The Discord bot instance, passed to setup functions.
        guild_id (Optional[int]): Guild ID for scoping specific modules.
        token (Optional[str]): Bot token, if needed for validation.

    Returns:
        None

    Notes:
        - Ensures dynamic module loading aligns with helper standards.
        - Logs the results of successful and failed module loads.
    """
    logger.info("Initializing Loading Helper setup...")
    try:
        results = await load_modules_from_directory(directory, module_type, bot, guild_id, token)  # Load modules.
        logger.info(f"Loading Helper setup completed. Results: {results}")  # Log results.
    except Exception as e:
        logger.error(f"Error during Loading Helper setup: {e}")  # Log errors.
        raise
