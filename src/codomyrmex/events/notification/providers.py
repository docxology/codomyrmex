"""
Notification Providers

Channel-specific notification delivery implementations.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
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

    @abstractmethod
    def send(self, notification: Notification) -> NotificationResult:
        """Send a notification."""


class ConsoleProvider(NotificationProvider):
    """Print notifications to console."""

    @property
    def channel(self) -> NotificationChannel:
        """Channel."""
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
        print(
            f"\n{prefix} [{notification.priority.value.upper()}] {notification.subject}"
        )
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
        self.file_path = file_path

    @property
    def channel(self) -> NotificationChannel:
        """Channel."""
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
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            return NotificationResult(
                notification_id=notification.id,
                status=NotificationStatus.FAILED,
                channel=self.channel,
                error=str(e),
            )


class WebhookProvider(NotificationProvider):
    """Deliver notifications by POSTing them as JSON to a webhook URL."""

    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
    ):
        scheme = urllib.parse.urlsplit(url).scheme
        if scheme not in ("http", "https"):
            raise ValueError(f"Webhook URL must use http or https, got {url!r}")
        self.url = url
        self.headers = headers or {}
        self.timeout = timeout

    @property
    def channel(self) -> NotificationChannel:
        """Channel."""
        return NotificationChannel.WEBHOOK

    def send(self, notification: Notification) -> NotificationResult:
        """POST ``notification.to_dict()`` as JSON; any 2xx response counts as sent."""
        body = json.dumps(notification.to_dict()).encode("utf-8")
        request = urllib.request.Request(
            self.url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", **self.headers},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                status_code = response.status
                response_body = response.read(65536).decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            return NotificationResult(
                notification_id=notification.id,
                status=NotificationStatus.FAILED,
                channel=self.channel,
                error=f"HTTP {e.code}: {e.reason}",
                response={"url": self.url, "status_code": e.code},
            )
        except (urllib.error.URLError, OSError, ValueError) as e:
            return NotificationResult(
                notification_id=notification.id,
                status=NotificationStatus.FAILED,
                channel=self.channel,
                error=str(e),
                response={"url": self.url},
            )

        return NotificationResult(
            notification_id=notification.id,
            status=NotificationStatus.SENT,
            channel=self.channel,
            sent_at=datetime.now(),
            response={
                "url": self.url,
                "status_code": status_code,
                "body": response_body,
            },
        )
