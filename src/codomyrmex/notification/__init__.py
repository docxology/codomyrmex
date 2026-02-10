"""
Notification Module

Multi-channel notification system with templates and routing.
"""

__version__ = "0.1.0"

from .models import (
    Notification,
    NotificationChannel,
    NotificationPriority,
    NotificationResult,
    NotificationStatus,
)
from .providers import ConsoleProvider, FileProvider, NotificationProvider, WebhookProvider
from .templates import (
    ALERT_TEMPLATE,
    ERROR_TEMPLATE,
    INFO_TEMPLATE,
    NotificationTemplate,
)
from .service import NotificationRouter, NotificationService

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
]
