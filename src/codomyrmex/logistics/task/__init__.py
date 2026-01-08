"""
Queue module for Codomyrmex.

This module provides task queue management, job scheduling, and async task execution.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from codomyrmex.exceptions import CodomyrmexError

from .job import Job, JobStatus
from .queue import Queue
from .scheduler import JobScheduler

__all__ = [
    "Queue",
    "Job",
    "JobStatus",
    "JobScheduler",
    "get_queue",
]

__version__ = "0.1.0"


class QueueError(CodomyrmexError):
    """Raised when queue operations fail."""

    pass


def get_queue(backend: str = "in_memory") -> Queue:
    """Get a queue instance.

    Args:
        backend: Queue backend (in_memory, redis)

    Returns:
        Queue instance
    """
    return Queue(backend=backend)


