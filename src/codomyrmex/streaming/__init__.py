"""
Streaming Module

Event streaming with in-memory, SSE, and topic-based backends.
"""

from .models import Event, EventType, Subscription, create_event
from .stream import (
    InMemoryStream,
    SSEStream,
    Stream,
    TopicStream,
    broadcast,
)
from .processors import StreamProcessor

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the streaming module."""
    return {
        "streams": {
            "help": "List active streams",
            "handler": lambda: print(
                "Stream Backends:\n"
                "  - InMemoryStream\n"
                "  - SSEStream\n"
                "  - TopicStream\n"
                "  Active streams: 0"
            ),
        },
        "stats": {
            "help": "Show streaming statistics",
            "handler": lambda: print(
                "Streaming Stats:\n"
                "  Event types:      " + str(len(EventType)) + "\n"
                "  Processors:       0\n"
                "  Subscriptions:    0"
            ),
        },
    }


__all__ = [
    "EventType",
    "Event",
    "Subscription",
    "create_event",
    "Stream",
    "InMemoryStream",
    "SSEStream",
    "TopicStream",
    "broadcast",
    "StreamProcessor",
    # CLI integration
    "cli_commands",
]
