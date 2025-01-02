"""
Asynchronous Helper Functions for Kasutamaiza Bot.
Version: 1.0.0
Author: ProfessorSeanEX
Purpose: Provide reusable utilities for managing asynchronous tasks, concurrency, and rate-limiting.

Updates:
- Enhanced timeout handling and retry logic.
- Added rate limiter and concurrency utilities.
- Integrated advanced task scheduling and cancellation management.
"""

import asyncio
from loguru import logger
from typing import Any, Coroutine, List

# --- Metadata ---
__version__ = "1.0.0"
__author__ = "ProfessorSeanEX"
__purpose__ = "Streamline async operations, task scheduling, concurrency handling, and rate limiting."

# --- Timeout Management ---
async def wait_with_timeout(coroutine: Coroutine, timeout: int) -> Any:
    """
    Waits for a coroutine to complete within a timeout period.

    Args:
        coroutine (Coroutine): The coroutine to wait for.
        timeout (int): Timeout period in seconds.

    Returns:
        Any: Result of the coroutine if completed, None if timed out.
    """
    try:
        result = await asyncio.wait_for(coroutine, timeout=timeout)
        logger.debug(f"Coroutine completed successfully within {timeout}s")
        return result
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout}s")
        return None

async def execute_with_timeout(coroutine: Coroutine, timeout: int) -> Any:
    """
    Executes a coroutine and raises an error if it times out.

    Args:
        coroutine (Coroutine): The coroutine to execute.
        timeout (int): Timeout period in seconds.

    Returns:
        Any: Result of the coroutine if completed.

    Raises:
        asyncio.TimeoutError: If the coroutine times out.
    """
    try:
        result = await asyncio.wait_for(coroutine, timeout=timeout)
        logger.debug(f"Coroutine executed successfully within {timeout}s")
        return result
    except asyncio.TimeoutError:
        logger.error(f"The operation exceeded the timeout of {timeout}s and was terminated.")
        raise asyncio.TimeoutError("The operation timed out.")

# --- Task Scheduling ---
async def schedule_task(coroutine: Coroutine, delay: int) -> None:
    """
    Schedules a coroutine to run after a delay.

    Args:
        coroutine (Coroutine): The coroutine to schedule.
        delay (int): Delay time in seconds before execution.

    Returns:
        None
    """
    logger.info(f"Scheduling task to execute after {delay}s delay.")
    await asyncio.sleep(delay)
    await coroutine

async def repeat_task(coro: Coroutine, interval: int, stop_event: asyncio.Event):
    """
    Repeats a task at regular intervals until stopped.

    Args:
        coro (Coroutine): The task to repeat.
        interval (int): Interval in seconds between task executions.
        stop_event (asyncio.Event): An event to signal when to stop repeating.

    Returns:
        None
    """
    logger.info(f"Starting repeated task every {interval}s.")
    while not stop_event.is_set():
        await coro
        await asyncio.sleep(interval)
    logger.info("Repeated task stopped.")

def create_task_with_logging(coroutine: Coroutine, task_name: str) -> asyncio.Task:
    """
    Creates and logs an asynchronous task for better traceability.

    Args:
        coroutine (Coroutine): The coroutine to execute as a task.
        task_name (str): A descriptive name for the task.

    Returns:
        asyncio.Task: The created task.
    """
    task = asyncio.create_task(coroutine)
    logger.info(f"Task '{task_name}' has been scheduled.")
    return task

# --- Rate Limiting ---
class RateLimiter:
    """
    Implements rate limiting for coroutines.
    """

    def __init__(self, max_calls: int, period: int):
        """
        Initializes the RateLimiter.

        Args:
            max_calls (int): Maximum number of calls allowed.
            period (int): Time period in seconds for rate limiting.
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        """
        Acquires permission to proceed based on rate limits.

        Returns:
            None
        """
        async with self.lock:
            current_time = asyncio.get_event_loop().time()
            self.calls = [call for call in self.calls if call > current_time - self.period]
            if len(self.calls) >= self.max_calls:
                sleep_time = self.calls[0] + self.period - current_time
                logger.info(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds.")
                await asyncio.sleep(sleep_time)
            self.calls.append(asyncio.get_event_loop().time())

# --- Concurrency Utilities ---
async def gather_with_concurrency(limit: int, *tasks: Coroutine) -> List[Any]:
    """
    Runs coroutines concurrently, with a limit on the number of simultaneous tasks.

    Args:
        limit (int): The maximum number of concurrent tasks.
        *tasks: The coroutines to execute.

    Returns:
        list[Any]: Results of the completed tasks.
    """
    semaphore = asyncio.Semaphore(limit)

    async def semaphore_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(semaphore_task(task) for task in tasks))

# --- Cancellation Management ---
async def cancel_task(task: asyncio.Task) -> None:
    """
    Cancels an asyncio task safely.

    Args:
        task (asyncio.Task): The task to cancel.

    Returns:
        None
    """
    if not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info("Task was successfully cancelled.")

# --- Retry Logic ---
async def retry_task(coro: Coroutine, retries: int, delay: int = 1) -> Any:
    """
    Retries a coroutine a specified number of times with a delay.

    Args:
        coro (Coroutine): The coroutine to retry.
        retries (int): Number of retry attempts.
        delay (int): Delay in seconds between retries.

    Returns:
        Any: Result of the coroutine if successful.

    Raises:
        Exception: If all retry attempts fail.
    """
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Attempt {attempt} for coroutine.")
            return await coro
        except Exception as e:
            logger.warning(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
    logger.error(f"All {retries} attempts failed.")
    raise

async def setup(*args, **kwargs):
    pass
