"""
Scheduling Helper for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Manage scheduled tasks, periodic updates, and reminders for bot operations.

Updates:
- Enhanced task scheduling with repeatable and one-time event capabilities.
- Improved error handling and logging for better traceability.
- Added utility functions to calculate next run times for tasks.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional
from loguru import logger

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Handle task scheduling and timed events efficiently."

# --- Task Scheduler Class ---
class TaskScheduler:
    """
    A class for scheduling and managing asynchronous tasks.
    """

    def __init__(self):
        """
        Initializes the TaskScheduler with an empty task registry.
        """
        self.tasks: Dict[str, asyncio.Task] = {}

    def schedule_task(self, task_name: str, coroutine: Callable, delay: int, repeat: bool = False):
        """
        Schedules a task to run after a delay and optionally repeat.

        Args:
            task_name (str): Unique name for the task.
            coroutine (Callable): The coroutine to execute.
            delay (int): Delay in seconds before execution.
            repeat (bool): Whether the task should repeat periodically.
        """
        async def task_runner():
            while True:
                await asyncio.sleep(delay)
                try:
                    logger.info(f"Executing task: {task_name}")
                    await coroutine()
                except Exception as e:
                    logger.error(f"Error in task '{task_name}': {e}")
                if not repeat:
                    break

        if task_name in self.tasks:
            logger.warning(f"Task '{task_name}' is already scheduled. Overwriting.")
        self.tasks[task_name] = asyncio.create_task(task_runner())
        logger.info(f"Task '{task_name}' scheduled to run in {delay} seconds. Repeat: {repeat}")

    def cancel_task(self, task_name: str):
        """
        Cancels a scheduled task.

        Args:
            task_name (str): The name of the task to cancel.
        """
        task = self.tasks.get(task_name)
        if task and not task.done():
            task.cancel()
            try:
                asyncio.run(task)
            except asyncio.CancelledError:
                logger.info(f"Task '{task_name}' cancelled successfully.")
            del self.tasks[task_name]
        else:
            logger.warning(f"Task '{task_name}' not found or already completed.")

    def list_tasks(self) -> List[str]:
        """
        Lists all active tasks.

        Returns:
            List[str]: Names of all scheduled tasks.
        """
        active_tasks = [name for name, task in self.tasks.items() if not task.done()]
        logger.info(f"Active tasks: {active_tasks}")
        return active_tasks

# --- Timed Events ---
async def schedule_timed_event(event_name: str, event_time: datetime, coroutine: Callable):
    """
    Schedules a one-time event to occur at a specific time.

    Args:
        event_name (str): Unique name for the event.
        event_time (datetime): The time at which the event should run.
        coroutine (Callable): The coroutine to execute.
    """
    now = datetime.now()
    delay = (event_time - now).total_seconds()
    if delay < 0:
        logger.error(f"Event '{event_name}' is scheduled for a past time.")
        return

    logger.info(f"Scheduling event '{event_name}' for {event_time}.")
    await asyncio.sleep(delay)
    try:
        logger.info(f"Executing event '{event_name}'.")
        await coroutine()
    except Exception as e:
        logger.error(f"Error in event '{event_name}': {e}")

# --- Utility Functions ---
def calculate_next_run(interval: int, start_time: Optional[datetime] = None) -> datetime:
    """
    Calculates the next run time for a task based on a given interval.

    Args:
        interval (int): Interval in seconds.
        start_time (Optional[datetime]): Starting time. Defaults to now.

    Returns:
        datetime: The next run time.
    """
    if not start_time:
        start_time = datetime.now()
    next_run = start_time + timedelta(seconds=interval)
    logger.info(f"Next run time calculated as {next_run}.")
    return next_run

async def setup(*args, **kwargs):
    pass
