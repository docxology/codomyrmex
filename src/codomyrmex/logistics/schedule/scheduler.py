"""
Main scheduler interface for advanced scheduling capabilities.
"""

import threading
import time
from collections.abc import Callable

from codomyrmex.logging_monitoring.logger_config import get_logger

from .cron import CronExpression, CronScheduler
from .recurring import RecurringSchedule, RecurringScheduler
from .timezone import TimezoneManager

logger = get_logger(__name__)


class ScheduleManager:
    """Main scheduler interface for managing scheduled tasks."""

    def __init__(self, timezone: str | None = None):
        """Initialize schedule manager.

        Args:
            timezone: Default timezone for scheduling (default: UTC)
        """
        self.timezone_manager = TimezoneManager(timezone)
        self.cron_scheduler = CronScheduler(self.timezone_manager)
        self.recurring_scheduler = RecurringScheduler(self.timezone_manager)
        self._scheduled_tasks: dict[str, dict] = {}
        self._running = False
        self._thread: threading.Thread | None = None

    def schedule_cron(
        self,
        task_id: str,
        cron_expression: str,
        callback: Callable,
        *args,
        **kwargs
    ) -> str:
        """Schedule a task using cron expression.

        Args:
            task_id: Unique identifier for the task
            cron_expression: Cron expression (e.g., "0 0 * * *" for daily at midnight)
            callback: Function to call when scheduled
            *args: Arguments to pass to callback
            **kwargs: Keyword arguments to pass to callback

        Returns:
            Task ID
        """
        cron = CronExpression.parse(cron_expression)
        self._scheduled_tasks[task_id] = {
            "type": "cron",
            "cron": cron,
            "callback": callback,
            "args": args,
            "kwargs": kwargs,
        }
        logger.info(f"Scheduled cron task {task_id} with expression {cron_expression}")
        return task_id

    def schedule_recurring(
        self,
        task_id: str,
        schedule: RecurringSchedule,
        callback: Callable,
        *args,
        **kwargs
    ) -> str:
        """Schedule a recurring task.

        Args:
            task_id: Unique identifier for the task
            schedule: RecurringSchedule instance
            callback: Function to call when scheduled
            *args: Arguments to pass to callback
            **kwargs: Keyword arguments to pass to callback

        Returns:
            Task ID
        """
        self._scheduled_tasks[task_id] = {
            "type": "recurring",
            "schedule": schedule,
            "callback": callback,
            "args": args,
            "kwargs": kwargs,
        }
        logger.info(f"Scheduled recurring task {task_id}")
        return task_id

    def cancel(self, task_id: str) -> bool:
        """Cancel a scheduled task.

        Args:
            task_id: Task identifier

        Returns:
            True if task was cancelled, False if not found
        """
        if task_id in self._scheduled_tasks:
            del self._scheduled_tasks[task_id]
            logger.info(f"Cancelled task {task_id}")
            return True
        return False

    def start(self, check_interval: int = 60) -> None:
        """Start the scheduler.

        Args:
            check_interval: Interval in seconds to check for scheduled tasks
        """
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._run, args=(check_interval,), daemon=True
        )
        self._thread.start()
        logger.info("Schedule manager started")

    def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Schedule manager stopped")

    def _run(self, check_interval: int) -> None:
        """Run the scheduler loop."""
        while self._running:
            try:
                now = self.timezone_manager.now()
                for task_id, task_info in list(self._scheduled_tasks.items()):
                    should_run = False

                    if task_info["type"] == "cron":
                        should_run = self.cron_scheduler.should_run(
                            task_info["cron"], now
                        )
                    elif task_info["type"] == "recurring":
                        should_run = self.recurring_scheduler.should_run(
                            task_info["schedule"], now
                        )

                    if should_run:
                        try:
                            task_info["callback"](*task_info["args"], **task_info["kwargs"])
                            logger.info(f"Executed scheduled task {task_id}")
                        except Exception as e:
                            logger.error(f"Error executing task {task_id}: {e}")

                time.sleep(check_interval)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(check_interval)

    def list_tasks(self) -> list[str]:
        """List all scheduled task IDs.

        Returns:
            List of task IDs
        """
        return list(self._scheduled_tasks.keys())


