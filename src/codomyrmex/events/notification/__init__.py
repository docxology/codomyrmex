"""
Notification Module

Multi-channel notification system with templates and routing.
"""

__version__ = "0.1.0"

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .models import (
    Notification,
    NotificationChannel,
    NotificationPriority,
    NotificationResult,
    NotificationStatus,
)
from .providers import (
    ConsoleProvider,
    FileProvider,
    NotificationProvider,
    WebhookProvider,
)
from .service import NotificationRouter, NotificationService
from .templates import (
    ALERT_TEMPLATE,
    ERROR_TEMPLATE,
    INFO_TEMPLATE,
    NotificationTemplate,
)


def cli_commands():
    """Return CLI commands for the notification module."""
    def _channels(**kwargs):
        """List notification channels."""
        print("=== Notification Channels ===")
        for channel in NotificationChannel:
            print(f"  {channel.value}")
        print("\nProviders:")
        print("  ConsoleProvider  - Print to stdout")
        print("  FileProvider     - Write to file")
        print("  WebhookProvider  - HTTP webhook delivery")

    def _send(**kwargs):
        """Send a notification with --message arg."""
        message = kwargs.get("message")
        if not message:
            print("Usage: notification send --message 'Your message here'")
            return
        provider = ConsoleProvider()
        notification = Notification(
            channel=NotificationChannel("console"),
            message=message,
            priority=NotificationPriority("normal") if hasattr(NotificationPriority, "__call__") else NotificationPriority.NORMAL,
        )
        result = provider.send(notification)
        status = result.status if hasattr(result, "status") else "sent"
        print(f"Notification {status}: {message}")

    return {
        "channels": {"handler": _channels, "help": "List notification channels"},
        "send": {"handler": _send, "help": "Send notification with --message arg"},
    }


__all__ = [
    # Enums
    "NotificationChannel",
    "NotificationPriority",
    "NotificationStatus",
    # Data classes
    "Notification",
    "NotificationResult",
    # Providers
    "NotificationProvider",
    "ConsoleProvider",
    "FileProvider",
    "WebhookProvider",
    # Core
    "NotificationTemplate",
    "NotificationRouter",
    "NotificationService",
    # Templates
    "ALERT_TEMPLATE",
    "INFO_TEMPLATE",
    "ERROR_TEMPLATE",
    "cli_commands",
]
