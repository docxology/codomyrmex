"""Gateway cron ticker for out-of-band tasks.

Uses asyncio.create_task to ensure I/O polling does not block the main event loop.
"""

import asyncio
from collections.abc import Callable
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class CronTicker:
    """Async cron service bursting background jobs on 60 second intervals."""

    def __init__(self, interval: float = 60.0) -> None:
        self.interval = interval
        self._running = False
        self._task: asyncio.Task[Any] | None = None
        self._jobs: list[Callable[[], Any]] = []

    def register_job(self, func: Callable[[], Any]) -> None:
        """Register a job to run every tick."""
        self._jobs.append(func)

    def start(self) -> None:
        """Start the ticker thread."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._ticker_loop())
        logger.info(f"CronTicker started with {self.interval}s interval.")

    def stop(self) -> None:
        """Stop the ticker."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("CronTicker stopped.")

    async def _execute_job(self, job: Callable[[], Any]) -> None:
        """Execute a single job gracefully without blocking others."""
        try:
            if asyncio.iscoroutinefunction(job):
                await job()
            else:
                job()
        except Exception as e:
            logger.error(f"Cron job error: {e}", exc_info=True)

    async def _ticker_loop(self) -> None:
        """The main tick loop firing bursts."""
        while self._running:
            await asyncio.sleep(self.interval)

            if not self._running:
                break

            # Fire all registered jobs off via create_task to prevent blocking!
            for job in self._jobs:
                asyncio.create_task(self._execute_job(job))
