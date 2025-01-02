# --- Metadata ---
"""
Environment Helper Functions for Kasutamaiza Bot.

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX
- Purpose: Centralized utilities for managing and validating environment variables.
"""
# Provides high-level context about the purpose and ownership of this file.

# --- Imports ---
"""
Necessary libraries and modules for utility discovery, initialization, and encapsulation.
"""
# Standard Library Imports
import os  # For managing environment variables.

# Third-Party Library Imports
from loguru import logger  # For logging environment variable operations.


# --- File Metadata Variables ---
"""
Defines key metadata about the file for tracking and debugging purposes.
"""
__version__ = "1.0.0"  # Current version of the Environment Helper module.
__author__ = "ProfessorSeanEX"  # Developer responsible for maintaining this module.
__purpose__ = "Provide utilities for managing and validating environment variables."  # Helper's purpose.


# --- Initialization ---
class EnvironmentHelper:
    """
    Provides utilities for managing and validating environment variables.
    """

    def __init__(self):
        """
        Initializes the Environment Helper.
        Logs the initialization process and registers priority helpers globally for compatibility.
        """
        logger.info("Initializing Environment Helper...")  # Log initialization.

        # Ensures backward compatibility by globally registering legacy helper functions.
        # Uncomment the lines below if legacy support is needed for older implementations.
        
        # globals()["validate_required_environment_variables"] = self.validate_required_environment_variables
        # globals()["fetch_environment_variable"] = self.fetch_environment_variable
        # globals()["list_environment_variables"] = self.list_environment_variables
        # globals()["set_default_environment_variable"] = self.set_default_environment_variable

        logger.info("Environment Helper initialized with legacy support.")  # Log completion.
        logger.debug(
            f"Environment Helper initialized with legacy support for functions: "
            f"{', '.join(['validate_required_environment_variables', 'fetch_environment_variable', 'list_environment_variables', 'set_default_environment_variable'])}"
        )


# --- Core Functionalities ---
    # --- Function [Fetch Environment Variable] ---
    def fetch_environment_variable(self, key: str, expected_type: type, default=None):
        """
        Fetches and validates an environment variable.

        Args:
            key (str): The name of the environment variable.
            expected_type (type): The type the variable value is expected to be.
            default: Default value if the variable is not set.

        Returns:
            The value of the environment variable, cast to the expected type, or the default value.
        """
        try:
            # Retrieve the value or use the default if not set.
            value = os.getenv(key, default)

            # If the variable is set, ensure its type matches the expected type.
            if value is not None and not isinstance(value, expected_type):
                # Cast the variable to the expected type.
                if expected_type is int:
                    value = int(value)
                elif expected_type is float:
                    value = float(value)
                elif expected_type is bool:
                    value = value.lower() in ("true", "1", "yes")
                elif expected_type is str:
                    value = str(value)

            # Log the successfully fetched and cast variable.
            logger.debug(f"Fetched environment variable {key}: {value} (Type: {expected_type.__name__})")
            return value
        except (ValueError, TypeError) as e:
            # Log a warning if parsing or casting fails.
            logger.warning(
                f"Failed to parse environment variable {key}. "
                f"Expected Type: {expected_type.__name__}, Default: {default}. Error: {e}"
            )
            return default


    # --- Function [Validate Required Environment Variables] ---
    def validate_required_environment_variables(self, required_vars: dict) -> dict:
        """
        Validates that all required environment variables are set and correctly typed.

        Args:
            required_vars (dict): A dictionary mapping variable names to their expected types.

        Returns:
            dict: A dictionary of validated environment variables and their values.

        Raises:
            RuntimeError: If any required environment variables are missing or invalid.
        """
        missing_vars = []  # List to track missing variables.
        valid_vars = {}  # Dictionary to store validated variables.
        logger.info("Validating required environment variables...")  # Log start of validation.

        for var_name, expected_type in required_vars.items():
            try:
                # Attempt to fetch and validate the variable.
                value = self.fetch_environment_variable(var_name, expected_type)
                if value is None:
                    raise ValueError(f"Environment variable '{var_name}' is not set or invalid.")

                # Store validated variable in the results dictionary.
                valid_vars[var_name] = value
                logger.debug(f"Validated environment variable: {var_name} = {value}")  # Log success.
            except Exception as e:
                # Add missing variable to the list and log the error.
                logger.error(f"Validation failed for '{var_name}': {e}")
                missing_vars.append(var_name)

        if missing_vars:
            # Raise an error if any required variables are missing.
            error_message = f"Missing or invalid environment variables: {', '.join(missing_vars)}"
            logger.error(error_message)
            raise RuntimeError(error_message)

        logger.info("All required environment variables validated successfully.")  # Log success.
        logger.info(f"Validation Summary: {len(valid_vars)} variables validated successfully, {len(missing_vars)} missing.")
        return valid_vars


# --- Utility Functionalities  ---
    # --- Function [List Environment Variables] ---
    def list_environment_variables(self) -> dict:
        """
        Lists all currently loaded environment variables.

        Returns:
            dict: A dictionary of all environment variables and their values.
        """
        try:
            # Collect all environment variables into a dictionary.
            env_vars = dict(os.environ)
            logger.debug(f"Environment variables snapshot: {list(env_vars.items())[:10]} (Showing first 10)")  # Log success.
            return env_vars
        except Exception as e:
            # Log an error if something goes wrong during listing.
            logger.error(f"Error in list_environment_variables: {e}")
            return {}

    # --- Function [Set Default Environment Variable] ---
    def set_default_environment_variable(self, key: str, value: str):
        """
        Sets a default value for an environment variable if it is not already set.

        Args:
            key (str): The name of the environment variable.
            value (str): The default value to set if the variable is not already defined.
        """
        try:
            # Check that inputs are strings for robustness.
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError(f"Both key and value must be strings. Got: {type(key)}, {type(value)}")

            if key not in os.environ:
                os.environ[key] = value
                logger.info(f"Set default {key}: {value}")
            else:
                logger.debug(f"{key} already exists; default not applied.")
        except Exception as e:
            logger.error(f"Error setting default {key}: {e}")


# --- Setup Method ---
async def setup(self, *args, **kwargs):
    """
    Setup function for Environment Helper.

     Logs metadata and confirms setup is complete.
     """
    logger.info("Environment Helper setup started.")
    try:
         # Log completion and metadata details.
        logger.info(f"Environment Helper setup completed. Metadata: Version={__version__}, Author={__author__}")
    except Exception as e:
         # Log errors during setup.
        logger.error(f"Environment Helper setup failed: {e}")
        raise
