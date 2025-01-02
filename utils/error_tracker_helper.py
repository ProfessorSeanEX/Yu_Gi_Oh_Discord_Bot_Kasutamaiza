"""
Error/Exception Tracker Helper for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Centralized tools for handling and analyzing errors and exceptions.

Updates:
- Enhanced logging of exceptions with detailed traceback information.
- Added optional alerting functionality for Discord channels.
- Integrated utility for summarizing recent exceptions from logs.
"""

from loguru import logger
import traceback
import datetime
import asyncio
from typing import Optional

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Streamline error tracking and logging with optional alerting capabilities."

# --- Core Error Tracking ---
def log_exception(exception: Exception, context: Optional[str] = None):
    """
    Logs an exception with optional context information.

    Args:
        exception (Exception): The exception object to log.
        context (str, optional): Additional context about where the exception occurred.

    Returns:
        None
    """
    error_message = f"Exception occurred: {exception}"
    if context:
        error_message += f" | Context: {context}"
    logger.error(error_message)
    logger.error("Traceback: " + "".join(traceback.format_exception(None, exception, exception.__traceback__)))

def capture_and_report_exception(exception: Exception, context: Optional[str] = None, alert_channel=None):
    """
    Captures an exception, logs it, and optionally reports it to a Discord channel.

    Args:
        exception (Exception): The exception to capture.
        context (str, optional): Additional context about where the exception occurred.
        alert_channel: The Discord channel to send the error report to (optional).

    Returns:
        None
    """
    log_exception(exception, context)
    if alert_channel:
        error_message = f"**Error Alert:**\n`{exception}`\n**Context:** {context or 'None provided'}"
        asyncio.create_task(alert_channel.send(error_message))

# --- Error Tracking Utilities ---
def summarize_exceptions(log_file: str, since_minutes: int = 60) -> list[str]:
    """
    Summarizes recent exceptions from the log file.

    Args:
        log_file (str): Path to the log file.
        since_minutes (int): Timeframe to search for exceptions in minutes.

    Returns:
        list[str]: Recent exceptions within the given timeframe.
    """
    exceptions = []
    try:
        cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=since_minutes)
        with open(log_file, "r") as file:
            for line in file:
                if "Exception occurred:" in line:
                    timestamp = extract_log_timestamp(line)
                    if timestamp and timestamp >= cutoff_time:
                        exceptions.append(line.strip())
    except Exception as e:
        log_exception(e, context="Error while summarizing exceptions")
    return exceptions

def extract_log_timestamp(log_line: str) -> Optional[datetime.datetime]:
    """
    Extracts the timestamp from a log line, if available.

    Args:
        log_line (str): The log line containing a timestamp.

    Returns:
        datetime.datetime or None: The extracted timestamp.
    """
    try:
        timestamp_part = log_line.split(" | ")[0]
        return datetime.datetime.strptime(timestamp_part, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return None

# --- Integration with Testing/Mocking (Optional Feature) ---
def simulate_exception_for_testing():
    """
    Simulates an exception for testing purposes.

    Returns:
        None
    """
    try:
        raise ValueError("This is a simulated exception for testing.")
    except Exception as e:
        log_exception(e, context="Simulated exception for testing")

async def setup(*args, **kwargs):
    pass
