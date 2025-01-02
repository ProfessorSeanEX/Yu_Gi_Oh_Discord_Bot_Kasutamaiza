"""
File Handling Helper Functions for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Provide utilities for managing file uploads, parsing, and storage for decks, logs, or card data.

Updates:
- Added robust JSON and CSV handling utilities.
- Integrated file validation and directory management.
- Enhanced error handling and logging for all operations.
"""

import os
import json
import csv
from typing import Optional, List, Dict
from loguru import logger

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Provide file handling utilities for uploads, parsing, and storage."

# --- File Path Utilities ---
def ensure_directory(directory: str):
    """
    Ensures a directory exists, creating it if necessary.

    Args:
        directory (str): The path of the directory.

    Returns:
        None
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Directory created: {directory}")
    else:
        logger.debug(f"Directory already exists: {directory}")

def delete_file(file_path: str):
    """
    Deletes a file if it exists.

    Args:
        file_path (str): The path of the file.

    Returns:
        None
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"File deleted: {file_path}")
    else:
        logger.warning(f"Attempted to delete non-existent file: {file_path}")

# --- JSON Handling ---
def read_json(file_path: str) -> Optional[Dict]:
    """
    Reads a JSON file and returns its contents.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        Optional[Dict]: Parsed JSON data or None if an error occurs.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            logger.info(f"JSON read successfully from {file_path}")
            return data
    except Exception as e:
        logger.error(f"Error reading JSON from {file_path}: {e}")
        return None

def write_json(file_path: str, data: Dict):
    """
    Writes data to a JSON file.

    Args:
        file_path (str): The path to the JSON file.
        data (Dict): The data to write.

    Returns:
        None
    """
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
            logger.info(f"JSON written successfully to {file_path}")
    except Exception as e:
        logger.error(f"Error writing JSON to {file_path}: {e}")

# --- CSV Handling ---
def read_csv(file_path: str) -> Optional[List[Dict]]:
    """
    Reads a CSV file and returns its contents as a list of dictionaries.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        Optional[List[Dict]]: Parsed CSV data or None if an error occurs.
    """
    try:
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            data = list(reader)
            logger.info(f"CSV read successfully from {file_path}")
            return data
    except Exception as e:
        logger.error(f"Error reading CSV from {file_path}: {e}")
        return None

def write_csv(file_path: str, data: List[Dict], fieldnames: List[str]):
    """
    Writes data to a CSV file.

    Args:
        file_path (str): The path to the CSV file.
        data (List[Dict]): The data to write.
        fieldnames (List[str]): The field names for the CSV file.

    Returns:
        None
    """
    try:
        with open(file_path, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            logger.info(f"CSV written successfully to {file_path}")
    except Exception as e:
        logger.error(f"Error writing CSV to {file_path}: {e}")

# --- File Validation ---
def validate_file_extension(file_name: str, allowed_extensions: List[str]) -> bool:
    """
    Validates a file's extension against a list of allowed extensions.

    Args:
        file_name (str): The name of the file.
        allowed_extensions (List[str]): The list of allowed file extensions.

    Returns:
        bool: True if the extension is allowed, False otherwise.
    """
    extension = os.path.splitext(file_name)[1].lower()
    if extension in allowed_extensions:
        logger.info(f"File '{file_name}' has a valid extension: {extension}")
        return True
    else:
        logger.warning(f"File '{file_name}' has an invalid extension: {extension}")
        return False

# --- File Upload and Parsing ---
def handle_file_upload(file_path: str, destination_dir: str, allowed_extensions: List[str]) -> Optional[str]:
    """
    Handles file uploads by validating and moving the file.

    Args:
        file_path (str): Path to the uploaded file.
        destination_dir (str): Directory to move the file to.
        allowed_extensions (List[str]): List of allowed file extensions.

    Returns:
        Optional[str]: The path to the moved file or None if validation fails.
    """
    file_name = os.path.basename(file_path)
    if validate_file_extension(file_name, allowed_extensions):
        ensure_directory(destination_dir)
        new_path = os.path.join(destination_dir, file_name)
        os.rename(file_path, new_path)
        logger.info(f"File uploaded successfully to {new_path}")
        return new_path
    else:
        logger.warning(f"File '{file_name}' failed validation and was not uploaded.")
        return None

async def setup(*args, **kwargs):
    pass
