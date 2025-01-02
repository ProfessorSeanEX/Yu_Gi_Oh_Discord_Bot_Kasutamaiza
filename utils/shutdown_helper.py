# --- Metadata ---
"""
Shutdown Helper for Kasutamaiza Bot.
Manages graceful shutdown procedures and resource cleanup.

Metadata:
- Version: 1.0.0
- Author: ProfessorSeanEX
- Purpose: Provide centralized functions for gracefully shutting down the bot and releasing resources.
"""


# --- Imports ---

# Standard Library Imports
import asyncio  # For managing asynchronous tasks and event loops.
import signal  # For handling operating system signals.
from typing import Callable, List, Optional  # Type annotations for arguments.

# Third-Party Library Imports
from loguru import logger  # Logging utility for diagnostics.

# --- Metadata [for the file] ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Provide centralized functions for gracefully shutting down the bot and releasing resources."


# --- Initialization ---
class ShutdownHelper:
    """
    Provides utilities for managing bot shutdown and resource cleanup.
    """

    def __init__(self, bot, db_manager: Optional[Callable] = None):
        """
        Initializes the Shutdown Helper.
        """
        self.bot = bot
        self.db_manager = db_manager
        self.tasks = []  # Holds additional cleanup tasks.
        logger.info("Shutdown Helper initialized.")


# --- Core Functionality: Shutdown ---
    async def shutdown_procedure(self):
        """
        Executes the shutdown procedure, closing resources and running tasks.

        Notes:
            - Closes the database connection pool if a db_manager is provided.
            - Executes additional cleanup tasks registered via register_task.
            - Ensures the event loop is stopped after cleanup for graceful termination.
        """
        logger.info("Starting shutdown procedure...")  # Log the initiation of the shutdown process.
        try:
            # Step 1: Close the database connection pool if the db_manager is available.
            if self.db_manager:
                logger.debug("Closing database connection pool.")  # Debug log before action.
                await self.db_manager.close_pool()
                logger.info("Database connection pool closed successfully.")  # Log success.

            # Step 2: Execute all registered cleanup tasks.
            for task in self.tasks:
                logger.info(f"Executing cleanup task: {task.__name__}")  # Log the task being executed.
                await task()  # Run the task.

            logger.info("Shutdown procedure completed successfully.")  # Log completion.
        except Exception as e:
            # Log any errors encountered during the shutdown process.
            logger.error(f"Error during shutdown procedure: {e}")
            raise  # Re-raise the exception for higher-level handling.
        finally:
            # Step 3: Stop the asyncio event loop for clean termination.
            logger.debug("Stopping asyncio event loop.")  # Debug log before stopping.
            asyncio.get_event_loop().stop()  # Stop the loop.

# --- Core Functionality: Graceful Shutdown ---
    async def graceful_shutdown(self):
        """
        Executes the shutdown procedure for the bot.

        Notes:
            - Invokes the shutdown_procedure for resource cleanup.
            - Acts as an entry point for signal-triggered shutdowns.
        """
        logger.info("Initiating graceful shutdown...")  # Log the start of graceful shutdown.

        try:
            # Call the shutdown procedure to clean up resources.
            await self.shutdown_procedure()
            logger.info("Graceful shutdown completed successfully.")  # Log completion.
        except Exception as e:
            # Log any errors encountered during the process.
            logger.error(f"Error during graceful shutdown: {e}")
            raise  # Re-raise the exception for higher-level handling.

# --- Core Functionality: Signal Handling ---
    def setup_signal_handlers(self):
        """
        Configures signal handlers for graceful shutdown.

        Notes:
            - Handles SIGINT (Ctrl+C) and SIGTERM signals.
            - Triggers the graceful_shutdown coroutine when signals are received.
        """
        # Ensure signal handlers are only configured once to avoid duplication.
        if getattr(signal, "_handlers_registered", False):
            logger.debug("Signal handlers already configured. Skipping setup.")  # Debug log for skipping.
            return
        signal._handlers_registered = True  # Mark handlers as registered.

        logger.info("Configuring signal handlers for graceful shutdown...")  # Log configuration start.

        def signal_handler(sig, frame):
            """
            Signal handler to invoke the shutdown process on receiving a signal.

            Args:
                sig: Signal number received.
                frame: Current stack frame at the time of the signal.
            """
            logger.info(f"Received signal {sig}. Triggering graceful shutdown.")  # Log signal reception.
            asyncio.run(self.graceful_shutdown())  # Run the graceful shutdown coroutine.

        # Bind signal handlers for termination signals.
        signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C interrupt.
        signal.signal(signal.SIGTERM, signal_handler)  # Handle termination signal.

        logger.info("Signal handlers configured successfully.")  # Log successful configuration.


# --- Utility Function: Task Registration ---
    def register_task(self, task: Callable):
        """
        Registers a cleanup task to execute during shutdown.

        Args:
            task (Callable): The task to register.

        Notes:
            - Tasks are stored in the tasks list and executed sequentially during shutdown.
            - This allows for modular and customizable cleanup processes.
        """
        self.tasks.append(task)  # Add the task to the list of cleanup tasks.
        logger.debug(f"Registered cleanup task: {task.__name__}")  # Log the registered task.


# --- Setup Method ---
async def setup(self):
    """
    Prepares the Shutdown Helper for use.

    Notes:
        - Configures signal handlers for graceful shutdown.
        - Ensures the helper is ready to manage termination signals and perform cleanup actions.
    """
    logger.info("Setting up Shutdown Helper...")  # Log the start of the setup process.

    # Configure signal handlers for graceful shutdown.
    logger.debug("Calling setup_signal_handlers to bind signal handlers.")  # Debug log for method call.
    self.setup_signal_handlers()

    logger.info("Shutdown Helper setup completed successfully.")  # Log successful setup.
