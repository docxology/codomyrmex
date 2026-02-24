"""
Notification Providers

Channel-specific notification delivery implementations.
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime

from .models import (
    Notification,
    NotificationChannel,
    NotificationPriority,
    NotificationResult,
    NotificationStatus,
)


class NotificationProvider(ABC):
    """Base class for notification providers."""

    @property
    @abstractmethod
    def channel(self) -> NotificationChannel:
        """Get the channel this provider handles."""
        pass

    @abstractmethod
    def send(self, notification: Notification) -> NotificationResult:
        """Send a notification."""
        pass


class ConsoleProvider(NotificationProvider):
    """Print notifications to console."""

    @property
    def channel(self) -> NotificationChannel:
        """Execute Channel operations natively."""
        return NotificationChannel.CONSOLE

    def send(self, notification: Notification) -> NotificationResult:
        """Print notification to console."""
        priority_prefix = {
            NotificationPriority.LOW: "ℹ️",
            NotificationPriority.MEDIUM: "📢",
            NotificationPriority.HIGH: "⚠️",
            NotificationPriority.CRITICAL: "🚨",
        }

        prefix = priority_prefix.get(notification.priority, "")
        print(f"\n{prefix} [{notification.priority.value.upper()}] {notification.subject}")
        print(f"   {notification.body}")

        return NotificationResult(
            notification_id=notification.id,
            status=NotificationStatus.SENT,
            channel=self.channel,
            sent_at=datetime.now(),
        )


class FileProvider(NotificationProvider):
    """Write notifications to a file."""

    def __init__(self, file_path: str = "notifications.log"):
        """Execute   Init   operations natively."""
        self.file_path = file_path

    @property
    def channel(self) -> NotificationChannel:
        """Execute Channel operations natively."""
        return NotificationChannel.FILE

    def send(self, notification: Notification) -> NotificationResult:
        """Write notification to file."""
        try:
            with open(self.file_path, "a") as f:
                line = json.dumps(notification.to_dict()) + "\n"
                f.write(line)

            return NotificationResult(
                notification_id=notification.id,
                status=NotificationStatus.SENT,
                channel=self.channel,
                sent_at=datetime.now(),
            )
        except Exception as e:
            return NotificationResult(
                notification_id=notification.id,
                status=NotificationStatus.FAILED,
                channel=self.channel,
                error=str(e),
            )


class WebhookProvider(NotificationProvider):
    """Send notifications via webhook."""

    def __init__(self, url: str, headers: dict[str, str] | None = None):
        """Execute   Init   operations natively."""
        self.url = url
        self.headers = headers or {}
        self._sent: list[Notification] = []  # Store for testing

    @property
    def channel(self) -> NotificationChannel:
        """Execute Channel operations natively."""
        return NotificationChannel.WEBHOOK

    def send(self, notification: Notification) -> NotificationResult:
        """Send notification via webhook."""
        self._sent.append(notification)

        # In real implementation, would use requests.post(self.url, ...)
        return NotificationResult(
            notification_id=notification.id,
            status=NotificationStatus.SENT,
            channel=self.channel,
            sent_at=datetime.now(),
            response={"url": self.url, "simulated": True},
        )
