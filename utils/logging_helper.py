# --- Metadata ---
"""
Logging Helper Functions for Kasutamaiza Bot.

Purpose:
- Provides centralized logging utilities for error tracking, performance monitoring, real-time alerts, and automated log management.

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX

Notes:
- This helper serves as the backbone for debugging, performance analysis, and operational insights.
- Log configurations include file rotation, diagnostics, and real-time alerting capabilities.
"""
# Provides high-level context about the purpose and ownership of this file.


# --- Imports ---
"""
Necessary libraries and modules for utility discovery, initialization, and encapsulation.
"""
# Standard Library Imports
import os  # For file and directory operations.
import asyncio  # To handle asynchronous log monitoring.
import logging  # Provides a secondary logging layer.
from pathlib import Path  # For managing log file paths.
from datetime import datetime, timezone  # For timestamping and timezone handling.

# Third-Party Library Imports
from loguru import logger  # Advanced logging with diagnostics and rotation.
import discord  # To interface with Discord's bot framework.


# --- File Metadata Variables ---
"""
Defines key metadata about the file for tracking and debugging purposes.
"""
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Enhance logging capabilities for error tracking, performance monitoring, real-time alerts, and automated log management."


# --- Initialization ---
class LoggingHelper:
    """
    A helper class for managing and enhancing logging functionalities.
    """

    LOG_DIR = Path("./logs")  # Directory for storing logs.
    DEFAULT_LOG_FILE = LOG_DIR / "bot.log"  # Default log file path.

    def __init__(self):
        """
        Initializes the logging helper with default configurations.
        """
        # Ensure the log directory exists.
        self.LOG_DIR.mkdir(exist_ok=True)

        # Configure logger with rotation, retention, and formatting.
        logger.add(
            self.DEFAULT_LOG_FILE,
            rotation="10 MB",  # Rotate logs after 10 MB.
            retention="7 days",  # Retain logs for 7 days.
            backtrace=True,  # Include traceback details.
            diagnose=True,  # Display variable values in tracebacks.
            enqueue=True,  # Thread-safe logging for async.
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
        )

        # Log the initialization of the logging helper.
        logger.info("Logging Helper initialized with file rotation and diagnostics.")


# --- Core Functionalities ---
    # --- Function [Log Error] ---
    def log_error(self, function_name: str, exception: Exception):
        """
        Logs detailed error information for debugging.

        Args:
            function_name (str): Name of the function where the error occurred.
            exception (Exception): Exception object with error details.
        """
        logger.error(
            f"Error in {function_name}: {exception} | "
            f"Timestamp: {datetime.utcnow().isoformat()} UTC", exc_info=True
        )

    # --- Function [Log Command] ---
    def log_command(self, ctx, command_name: str):
        """
        Logs command execution details, including user and guild context.

        Args:
            ctx: The command context or bot object.
            command_name (str): The command executed.
        """
        user = getattr(ctx, "user", "Unknown User")  # Fallback for user.
        guild = getattr(ctx, "guild", None)  # Fallback for guild context.

        guild_info = guild.name if guild else "Global/DM"
        logger.info(
            f"Command Executed: {command_name} | User: {user} | Guild: {guild_info} | "
            f"Timestamp: {datetime.utcnow().isoformat()} UTC"
        )

    # --- Function [Log Command Error] ---
    def log_command_error(self, command_name: str, ctx, exception: Exception):
        """
        Logs error details for failed command executions.

        Args:
            command_name (str): Name of the command where the error occurred.
            ctx: The context of the command.
            exception (Exception): The exception that occurred.
        """
        logger.error(
            f"Command Error: {command_name} | User: {ctx.user} | Channel: {ctx.channel} | "
            f"Guild: {ctx.guild} | Exception: {exception} | Timestamp: {datetime.utcnow().isoformat()} UTC"
        )

    # --- Function [Log Command Registration] ---
    def log_command_registration(command, cog_name: str, category: str):
        """
        Logs the registration of a command to a cog with its category.

        Args:
            command: The command being registered.
            cog_name (str): The name of the cog to which the command belongs.
            category (str): The category of the command.

        Returns:
            None

        Example:
            log_command_registration(my_command, "GeneralCog", "Utility")
        """
        # Log the registration of the command with its metadata.
        logger.debug(
            f"Command Registered: {command.name} | Cog: {cog_name} | Category: {category} | "
            f"Timestamp: {datetime.utcnow().isoformat()} UTC"
        )

    # --- Function [Log Command Registration] ---
    def log_command_registration(command, cog_name: str, category: str):
        """
        Logs the registration of a command to a cog with its category.

        Args:
            command: The command being registered.
            cog_name (str): The name of the cog to which the command belongs.
            category (str): The category of the command.

        Returns:
            None

        Example:
            log_command_registration(my_command, "GeneralCog", "Utility")
        """
        # Log the registration of the command with its metadata.
        logger.debug(
            f"Command Registered: {command.name} | Cog: {cog_name} | Category: {category} | "
            f"Timestamp: {datetime.utcnow().isoformat()} UTC"
        )


# --- Real-Time Monitoring Functionalities ---
    # --- Function [Monitor Logs for Alerts] ---
    async def monitor_logs_for_alerts(self, bot, channel_id: int, file_path: str, keywords: list[str]):
        """
        Monitors a log file for specific keywords and sends alerts if they appear.

        Args:
            bot (discord.Bot): The bot instance responsible for sending alerts.
            channel_id (int): The ID of the channel to send alerts to.
            file_path (str): The path to the log file to monitor.
            keywords (list[str]): List of keywords to trigger alerts.

        Returns:
            None
        """
        logger.info(f"Initializing log monitoring for file: {file_path} | Channel ID: {channel_id}")
        try:
            # Open the log file for reading in real-time.
            with open(file_path, "r") as log_file:
                # Move file pointer to the end to start monitoring new logs only.
                log_file.seek(0, os.SEEK_END)

                # Continuously monitor the log file for updates.
                while True:
                    line = log_file.readline()
                    if not line:  # If no new line, wait briefly before checking again.
                        await asyncio.sleep(1)
                        continue

                    # Check if the current line contains any of the specified keywords.
                    if any(keyword in line for keyword in keywords):
                        # Construct the alert message with the relevant log details.
                        alert_msg = (
                            f"⚠️ **Log Alert:** {line.strip()} (Detected at {datetime.utcnow().isoformat()} UTC)"
                        )
                        # Send the alert to the specified Discord channel.
                        await bot.get_channel(channel_id).send(alert_msg)
        except FileNotFoundError:
            # Log an error if the specified log file is not found.
            logger.error(f"Log file not found: {file_path}")
        except Exception as e:
            # Log any unexpected errors encountered during monitoring.
            self.log_error("monitor_logs_for_alerts", e)


# --- Log Extraction Functionalities ---
    # --- Function [Extract Error Logs] ---
    def extract_error_logs(self, file_path: str, severity: str = "ERROR", lines: int = 10) -> str:
        """
        Extracts recent log entries of a specified severity from a log file.

        Args:
            file_path (str): Path to the log file.
            severity (str): Log severity to filter by (e.g., "ERROR", "CRITICAL").
            lines (int): Number of recent lines to return.

        Returns:
            str: Filtered log entries as a string.
        """
        logger.info(f"Extracting '{severity}' logs from {file_path} | Last {lines} entries.")
        try:
            # Open the specified log file for reading.
            with open(file_path, "r") as log_file:
                # Filter the log file for entries matching the specified severity.
                filtered_logs = [line.strip() for line in log_file if severity in line]

                # Get the last 'lines' entries for the specified severity.
                result = "\n".join(filtered_logs[-lines:])
                logger.debug(f"Extracted {len(filtered_logs)} '{severity}' entries. Returning {lines}.")
                return result
        except FileNotFoundError:
            # Log an error if the log file is not found.
            logger.error(f"Log file not found: {file_path}")
            return f"Error: Log file '{file_path}' not found."
        except Exception as e:
            # Log unexpected errors and return an error message.
            self.log_error("extract_error_logs", e)
            return "Error: Unable to extract logs."


# --- Uptime and Performance Logging Section ---
    # --- Function [Log Uptime] ---
    def log_uptime(self, start_time: datetime):
        """
        Logs the bot's uptime since the provided start time.

        Args:
            start_time (datetime): The bot's start time. Must be a valid datetime object.
        """
        try:
            # Get the current time in UTC.
            current_time = datetime.now(timezone.utc)

            # Ensure the start_time is timezone-aware. If naive, assume UTC.
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)

            # Calculate the total uptime as the difference between current and start times.
            uptime = current_time - start_time

            # Format uptime for readability by removing microseconds.
            formatted_uptime = str(uptime).split(".")[0]

            # Log the calculated uptime with both start and current timestamps.
            logger.info(
                f"Bot Uptime: {formatted_uptime} | Started at: {start_time.isoformat()} | "
                f"Current Time: {current_time.isoformat()} UTC"
            )
        except Exception as e:
            # Log any errors encountered while calculating uptime.
            self.log_error("log_uptime", e)

    # --- Function [Log Query Performance] ---
    def log_query_performance(self, query: str, execution_time: float, rows_affected: int):
        """
        Logs the performance metrics of a database query.

        Args:
            query (str): The SQL query executed.
            execution_time (float): Time taken to execute the query in seconds.
            rows_affected (int): Number of rows affected by the query.
        """
        # Log the performance details, including execution time and affected rows.
        logger.info(
            f"Query Performance: Executed in {execution_time:.2f} seconds | Rows Affected: {rows_affected} | "
            f"Query: {query} | Timestamp: {datetime.utcnow().isoformat()} UTC"
        )
    
    # --- Function [Log Database Interaction] ---
    def log_database_interaction(query: str, parameters: list = None):
        """
        Logs database queries for debugging purposes.

        Args:
            query (str): The SQL query being executed.
            parameters (list, optional): Parameters for the SQL query. Defaults to None.

        Returns:
            None

        Example:
            log_database_interaction("SELECT * FROM users WHERE id = %s", [123])
        """
        # Format the parameters for readability, or use "None" if no parameters are provided.
        param_str = ", ".join(map(str, parameters)) if parameters else "None"

        # Log the interaction with query and parameters.
        logger.debug(
            f"Database Interaction: Executing query: {query} | Parameters: {param_str} | "
            f"Timestamp: {datetime.utcnow().isoformat()} UTC"
        )


# --- Automated Log Management Functionalities ---
    # --- Function [Auto Cleanup Logs] ---
    def auto_cleanup_logs(self, directory: str, archive_dir: str, max_size_mb: int):
        """
        Automatically cleans up log files by archiving them if the directory exceeds the specified size.

        Args:
            directory (str): Path to the directory containing log files.
            archive_dir (str): Path to the directory where logs will be archived.
            max_size_mb (int): Maximum allowed size for the log directory in MB.
        """
        logger.info(
            f"Starting log cleanup process | Directory: {directory} | Archive Directory: {archive_dir} | Max Size: {max_size_mb} MB"
        )
        try:
            # Calculate the total size of the log directory in bytes.
            total_size = sum(
                os.path.getsize(os.path.join(directory, f))
                for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f))
            )
            logger.debug(f"Total log directory size: {total_size / (1024 * 1024):.2f} MB")

            # If the directory size exceeds the specified limit, archive the files.
            if total_size > max_size_mb * 1024 * 1024:
                archived_logs = 0
                for log_file in os.listdir(directory):
                    file_path = os.path.join(directory, log_file)
                    if os.path.isfile(file_path):
                        # Move the file to the archive directory.
                        archive_path = os.path.join(archive_dir, log_file)
                        os.rename(file_path, archive_path)
                        archived_logs += 1
                logger.info(
                    f"Archived {archived_logs} log files from {directory} to {archive_dir} | "
                    f"Total Size Before Cleanup: {total_size / (1024 * 1024):.2f} MB"
                )
            else:
                logger.info("Log directory size is within limits. No cleanup required.")
        except FileNotFoundError:
            # Log an error if the specified directories are not found.
            logger.error(f"Log directory or archive directory not found | Directory: {directory} | Archive Directory: {archive_dir}")
        except Exception as e:
            # Log unexpected errors and alert the user.
            self.log_error("auto_cleanup_logs", e)

    # --- Function [Aggregate Logs] ---
    def aggregate_logs(self, log_files: list[str], output_file: str):
        """
        Combines multiple log files into a single output file for analysis.

        Args:
            log_files (list[str]): List of log file paths to aggregate.
            output_file (str): Path to the output aggregated log file.
        """
        logger.info(f"Starting log aggregation process | Output File: {output_file}")
        try:
            # Open the output file for writing aggregated log data.
            with open(output_file, "w") as outfile:
                for log_file in log_files:
                    # Check if each log file exists before processing.
                    if os.path.exists(log_file):
                        with open(log_file, "r") as infile:
                            outfile.write(infile.read())
                            logger.info(f"Aggregated logs from: {log_file}")
                    else:
                        # Log a warning for any missing log files.
                        logger.warning(f"Log file not found: {log_file}")
            logger.info(f"Log aggregation completed successfully | Output: {output_file}")
        except Exception as e:
            # Log unexpected errors during the aggregation process.
            self.log_error("aggregate_logs", e)
            logger.error("Log aggregation process failed.")


# --- Custom Logging Functionalities ---
    # --- Function [Log Custom] ---
    def log_custom(self, level: str, message: str):
        """
        Logs a message at a specified custom log level.

        Args:
            level (str): The log level (e.g., "CRITICAL", "DEBUG", "NOTICE").
            message (str): The log message to record.
        """
        # Map custom log levels to their corresponding logger methods.
        custom_levels = {
            "CRITICAL": logger.critical,
            "NOTICE": logger.info,
            "DEBUG": logger.debug,
            "INFO": logger.info,
            "WARNING": logger.warning,
            "ERROR": logger.error,
        }

        # Retrieve the appropriate logging method based on the provided level.
        log_func = custom_levels.get(level.upper(), logger.info)
        log_func(f"Custom Log | Level: {level.upper()} | Message: {message}")


# --- Debugging Tools Functionalities ---
    # --- Function [Log Registered Commands] ---
    def log_registered_commands(self, bot: discord.Bot):
        """
        Logs all registered slash commands for debugging and validation purposes.

        Args:
            bot (discord.Bot): The bot instance.
        """
        logger.info("Retrieving all registered slash commands...")  # Log the start of command retrieval.

        try:
            # Check if the bot has any registered application commands.
            if not bot.application_commands:
                logger.warning("No slash commands are currently registered with the bot.")
                return  # Exit the function if no commands are found.

            # Iterate through each command and log its metadata.
            for cmd in bot.application_commands:
                # Retrieve associated guilds or default to 'Global'.
                guild_ids = cmd.guild_ids or ["Global"]
                logger.info(
                    f"Registered Command: {cmd.name} | Description: {cmd.description} | "
                    f"Guilds: {', '.join(map(str, guild_ids))} | Timestamp: {datetime.utcnow().isoformat()} UTC"
                )
        except Exception as e:
            # Log unexpected errors during the process.
            self.log_error("log_registered_commands", e)
            logger.debug("Ensure all commands are correctly registered and valid.")  # Provide debugging tips.


# --- Utility Logging Functionalities ---
    # --- Function [Redact Sensitive Data] ---
    def redact_sensitive_data(log_entry: str, patterns: dict) -> str:
        """
        Redacts sensitive information from a log entry based on provided patterns.

        Args:
            log_entry (str): The log entry to be sanitized.
            patterns (dict): A dictionary of patterns to replace with their redacted forms.
                            Example: {"BOT_TOKEN": "REDACTED_TOKEN", "PASSWORD": "REDACTED_PASSWORD"}

        Returns:
            str: The sanitized log entry.

        Example:
            redact_sensitive_data(
                "Connecting with BOT_TOKEN=12345", {"BOT_TOKEN": "REDACTED_TOKEN"}
            )
        """
        try:
            # Iterate over the patterns and replace sensitive data in the log entry.
            for key, replacement in patterns.items():
                log_entry = log_entry.replace(key, replacement)

            logger.debug(f"Redacted sensitive data in log entry.")
            return log_entry
        except Exception as e:
            # Log any errors encountered during redaction.
            log_error("redact_sensitive_data", e)
            return log_entry  # Return the original log entry if redaction fails.
    
    # --- Function [Compress Logs] ---
    def compress_logs(directory: str, output_file: str):
        """
        Compresses all logs in a directory into a single archive file.

        Args:
            directory (str): Path to the directory containing log files.
            output_file (str): Path to the output archive file.

        Returns:
            None
        """
        import zipfile

        # Log the start of the compression process, including directory and output file details.
        logger.info(f"Starting log compression for directory: {directory} | Output File: {output_file}")
        try:
            # Open a new ZIP file for writing and iterate over all files in the directory.
            with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as archive:
                for log_file in os.listdir(directory):
                    file_path = os.path.join(directory, log_file)
                    
                    # Check if the current path is a file before adding to the archive.
                    if os.path.isfile(file_path):
                        archive.write(file_path, arcname=os.path.basename(file_path))
                        
                        # Log each successfully compressed file for traceability.
                        logger.debug(f"Compressed log file: {file_path}")
            
            # Log the successful completion of the compression process.
            logger.info(f"Log compression completed successfully. Archive created at: {output_file}")
        except Exception as e:
            # Log any unexpected errors for debugging and re-raise them.
            log_error("compress_logs", e)

    # --- Function [Monitor Error Threshold] ---
    async def monitor_error_threshold(bot, channel_id: int, file_path: str, error_count: int):
        """
        Monitors a log file for exceeding a specified error threshold and sends alerts.

        Args:
            bot (discord.Bot): The bot instance responsible for sending alerts.
            channel_id (int): The ID of the channel to send alerts to.
            file_path (str): The path to the log file to monitor.
            error_count (int): The threshold for the number of errors.

        Returns:
            None
        """
        # Log the initialization of error monitoring, including the threshold and file details.
        logger.info(f"Monitoring error threshold in file: {file_path} | Threshold: {error_count}")
        try:
            # Track the current error count during monitoring.
            current_count = 0
            
            # Open the log file for real-time monitoring.
            with open(file_path, "r") as log_file:
                log_file.seek(0, os.SEEK_END)  # Move to the end of the file to monitor new logs.
                
                while True:
                    line = log_file.readline()
                    
                    # Wait briefly for new log entries if none are available.
                    if not line:
                        await asyncio.sleep(1)
                        continue
                    
                    # Increment the error count if the line contains the "ERROR" keyword.
                    if "ERROR" in line:
                        current_count += 1
                    
                    # If the error threshold is reached, send an alert and reset the count.
                    if current_count >= error_count:
                        alert_msg = f"⚠️ Error threshold exceeded: {current_count} errors detected in {file_path}!"
                        
                        # Send the alert to the specified Discord channel.
                        await bot.get_channel(channel_id).send(alert_msg)
                        
                        # Reset the error count after sending the alert.
                        current_count = 0
        except Exception as e:
            # Log any errors encountered during monitoring for debugging purposes.
            log_error("monitor_error_threshold", e)

    # --- Function [Search Logs] ---
    def search_logs(file_path: str, query: str) -> list[str]:
        """
        Searches for a specific query in a log file and returns matching lines.

        Args:
            file_path (str): The path to the log file.
            query (str): The search query.

        Returns:
            list[str]: A list of log entries matching the query.
        """
        # Log the search operation, including the query and file being searched.
        logger.info(f"Searching log file: {file_path} for query: '{query}'")
        try:
            results = []
            
            # Open the log file and filter for lines containing the query.
            with open(file_path, "r") as log_file:
                results = [line.strip() for line in log_file if query in line]
            
            # Log the number of matching entries found.
            logger.debug(f"Found {len(results)} matching entries for query: '{query}'")
            return results
        except Exception as e:
            # Log any errors encountered during the search process.
            log_error("search_logs", e)
            return []

    # --- Function [Set Log Level] ---
    def set_log_level(level: str):
        """
        Dynamically sets the logging level for the application.

        Args:
            level (str): The desired log level (e.g., "DEBUG", "INFO", "WARNING").

        Returns:
            None
        """
        # Convert the level to uppercase for consistency and validation.
        level = level.upper()
        
        # Define a mapping of log levels to their respective functions.
        loguru_levels = {
            "DEBUG": logger.debug,
            "INFO": logger.info,
            "WARNING": logger.warning,
            "ERROR": logger.error,
            "CRITICAL": logger.critical,
        }
        try:
            # Validate and set the desired log level if valid.
            if level in loguru_levels:
                logger.info(f"Setting log level to: {level}")
                logging.getLogger().setLevel(level)
            else:
                # Raise an error if the log level is invalid.
                raise ValueError(f"Invalid log level: {level}")
        except Exception as e:
            # Log any errors encountered during log level setting.
            log_error("set_log_level", e)


# --- Setup Method ---
async def setup(*args, **kwargs):
    """
    Setup function for `utils.logging_helper`.
    Ensures that logging configurations and helpers are ready for use.

    Args:
        *args: Positional arguments (ignored in this context).
        **kwargs: Keyword arguments (ignored in this context).

    Raises:
        Exception: If setup fails.
    """
    logger.info("Setting up Logging Helper...")
    try:
        logger.info(f"Logging Helper setup completed. Metadata: Version={__version__}, Author={__author__}, Purpose={__purpose__}")
    except Exception as e:
        logger.error(f"Error during Logging Helper setup: {e}")
        raise
