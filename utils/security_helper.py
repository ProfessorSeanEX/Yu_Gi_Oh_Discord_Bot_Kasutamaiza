"""
Security Helper Functions for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Enhance bot security by providing tools for validation, encryption, and access control.

Updates:
- Improved input validation and sanitization.
- Added secure hashing, HMAC generation/verification, and access control utilities.
- Introduced a rate limiter class for command throttling.
- Enhanced logging for better security event tracking.
"""

import hashlib
import hmac
import secrets
from typing import Optional
from loguru import logger

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Provide utilities for securing data, validating inputs, and managing access control."

# --- Input Validation ---
def sanitize_input(input_data: str) -> str:
    """
    Sanitizes user input to prevent injection attacks.

    Args:
        input_data (str): The user-provided input.

    Returns:
        str: Sanitized input.
    """
    sanitized = input_data.replace("'", "").replace('"', "").replace(";", "").replace("--", "")
    logger.debug(f"Sanitized input: {sanitized}")
    return sanitized

def validate_input_length(input_data: str, max_length: int) -> bool:
    """
    Validates that the input does not exceed a maximum length.

    Args:
        input_data (str): The user-provided input.
        max_length (int): Maximum allowed length.

    Returns:
        bool: True if valid, False otherwise.
    """
    if len(input_data) > max_length:
        logger.warning(f"Input exceeds maximum length of {max_length}: {input_data}")
        return False
    return True

# --- Encryption and Hashing ---
def generate_secure_hash(data: str, salt: Optional[str] = None) -> str:
    """
    Generates a secure hash for the given data using SHA-256.

    Args:
        data (str): The data to hash.
        salt (str, optional): An optional salt for added security.

    Returns:
        str: The hashed data.
    """
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + data).encode()).hexdigest()
    logger.debug(f"Generated secure hash for data: {hashed}")
    return hashed

def verify_hash(data: str, hashed: str, salt: str) -> bool:
    """
    Verifies that the given data matches the hashed value when using the salt.

    Args:
        data (str): The original data.
        hashed (str): The hashed value.
        salt (str): The salt used during hashing.

    Returns:
        bool: True if verified, False otherwise.
    """
    return generate_secure_hash(data, salt) == hashed

# --- HMAC Verification ---
def generate_hmac(secret_key: str, message: str) -> str:
    """
    Generates an HMAC for the given message using a secret key.

    Args:
        secret_key (str): The secret key.
        message (str): The message to hash.

    Returns:
        str: The generated HMAC.
    """
    hmac_value = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
    logger.debug(f"Generated HMAC: {hmac_value}")
    return hmac_value

def verify_hmac(secret_key: str, message: str, hmac_to_verify: str) -> bool:
    """
    Verifies the HMAC for a message.

    Args:
        secret_key (str): The secret key.
        message (str): The message to verify.
        hmac_to_verify (str): The HMAC to verify.

    Returns:
        bool: True if verified, False otherwise.
    """
    calculated_hmac = generate_hmac(secret_key, message)
    is_verified = hmac.compare_digest(calculated_hmac, hmac_to_verify)
    logger.debug(f"HMAC verification result: {is_verified}")
    return is_verified

# --- Access Control ---
def check_user_permission(user_roles: list[str], required_roles: list[str]) -> bool:
    """
    Checks if a user has the required roles for access.

    Args:
        user_roles (list[str]): Roles assigned to the user.
        required_roles (list[str]): Roles required for access.

    Returns:
        bool: True if access is granted, False otherwise.
    """
    has_permission = any(role in required_roles for role in user_roles)
    if not has_permission:
        logger.warning("Access denied. User does not have the required roles.")
    return has_permission

# --- Rate Limiting ---
class RateLimiter:
    """
    Implements a simple rate limiter for commands.
    """

    def __init__(self, max_calls: int, period: int):
        """
        Initializes the rate limiter.

        Args:
            max_calls (int): Maximum number of calls allowed.
            period (int): Time period in seconds.
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = {}

    def is_limited(self, user_id: int) -> bool:
        """
        Checks if a user is rate-limited.

        Args:
            user_id (int): The user's ID.

        Returns:
        bool: True if limited, False otherwise.
        """
        now = secrets.token_hex(16)
        if user_id not in self.calls:
            self.calls[user_id] = []
        self.calls[user_id] = [call_time for call_time in self.calls[user_id] if now - call_time < self.period]
        if len(self.calls[user_id]) >= self.max_calls:
            logger.info(f"User {user_id} is rate-limited.")
            return True
        self.calls[user_id].append(now)
        return False

# --- Security Logging ---
def log_security_event(event_type: str, message: str):
    """
    Logs a security-related event.

    Args:
        event_type (str): Type of security event (e.g., "Access Denied", "Invalid Input").
        message (str): Detailed message about the event.

    Returns:
        None
    """
    logger.warning(f"Security Event - {event_type}: {message}")


async def setup(*args, **kwargs):
    pass
