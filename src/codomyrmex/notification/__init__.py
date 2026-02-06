"""
Notification Module

Multi-channel notification system with templates and routing.
"""

__version__ = "0.1.0"

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar
from collections.abc import Callable


class NotificationChannel(Enum):
    """Available notification channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    CONSOLE = "console"
    FILE = "file"


class NotificationPriority(Enum):
    """Priority levels for notifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationStatus(Enum):
    """Status of a notification."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"


@dataclass
class Notification:
    """A notification to be sent."""
    id: str
    subject: str
    body: str
    channel: NotificationChannel = NotificationChannel.CONSOLE
    priority: NotificationPriority = NotificationPriority.MEDIUM
    recipient: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "subject": self.subject,
            "body": self.body,
            "channel": self.channel.value,
            "priority": self.priority.value,
            "recipient": self.recipient,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class NotificationResult:
    """Result of sending a notification."""
    notification_id: str
    status: NotificationStatus
    channel: NotificationChannel
    sent_at: datetime | None = None
    error: str | None = None
    response: dict[str, Any] | None = None

    @property
    def is_success(self) -> bool:
        return self.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED]


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
        self.file_path = file_path

    @property
    def channel(self) -> NotificationChannel:
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
    """Send notifications via webhook (mock for testing)."""

    def __init__(self, url: str, headers: dict[str, str] | None = None):
        self.url = url
        self.headers = headers or {}
        self._sent: list[Notification] = []  # Store for testing

    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.WEBHOOK

    def send(self, notification: Notification) -> NotificationResult:
        """Send notification via webhook (mock)."""
        self._sent.append(notification)

        # In real implementation, would use requests.post(self.url, ...)
        return NotificationResult(
            notification_id=notification.id,
            status=NotificationStatus.SENT,
            channel=self.channel,
            sent_at=datetime.now(),
            response={"url": self.url, "simulated": True},
        )


class NotificationTemplate:
    """
    Template for generating notifications.

    Usage:
        template = NotificationTemplate(
            name="alert",
            subject_template="Alert: {type} - {severity}",
            body_template="An alert was triggered:\n\nType: {type}\nSeverity: {severity}\nMessage: {message}",
        )

        notification = template.render(
            id="alert_123",
            type="CPU",
            severity="HIGH",
            message="CPU usage exceeded 90%",
        )
    """

    def __init__(
        self,
        name: str,
        subject_template: str,
        body_template: str,
        default_channel: NotificationChannel = NotificationChannel.CONSOLE,
        default_priority: NotificationPriority = NotificationPriority.MEDIUM,
    ):
        self.name = name
        self.subject_template = subject_template
        self.body_template = body_template
        self.default_channel = default_channel
        self.default_priority = default_priority

    def render(
        self,
        id: str,
        channel: NotificationChannel | None = None,
        priority: NotificationPriority | None = None,
        recipient: str | None = None,
        **variables,
    ) -> Notification:
        """Render the template into a notification."""
        subject = self.subject_template.format(**variables)
        body = self.body_template.format(**variables)

        return Notification(
            id=id,
            subject=subject,
            body=body,
            channel=channel or self.default_channel,
            priority=priority or self.default_priority,
            recipient=recipient,
            metadata={"template": self.name, "variables": variables},
        )


class NotificationRouter:
    """
    Route notifications based on rules.

    Usage:
        router = NotificationRouter()

        # Route critical alerts to Slack
        router.add_rule(
            lambda n: n.priority == NotificationPriority.CRITICAL,
            NotificationChannel.SLACK,
        )

        # Route all others to console
        router.add_default(NotificationChannel.CONSOLE)
    """

    def __init__(self):
        self._rules: list[tuple] = []  # (condition, channel)
        self._default: NotificationChannel = NotificationChannel.CONSOLE

    def add_rule(
        self,
        condition: Callable[[Notification], bool],
        channel: NotificationChannel,
    ) -> "NotificationRouter":
        """Add a routing rule."""
        self._rules.append((condition, channel))
        return self

    def add_default(self, channel: NotificationChannel) -> "NotificationRouter":
        """Set default channel."""
        self._default = channel
        return self

    def route(self, notification: Notification) -> NotificationChannel:
        """Determine channel for notification."""
        for condition, channel in self._rules:
            if condition(notification):
                return channel
        return self._default


class NotificationService:
    """
    Central notification service.

    Usage:
        service = NotificationService()
        service.register_provider(ConsoleProvider())
        service.register_provider(SlackProvider(webhook_url))

        # Send directly
        result = service.send(Notification(
            id="123",
            subject="Test",
            body="Hello world",
        ))

        # Or with template
        template = NotificationTemplate(
            name="alert",
            subject_template="Alert: {type}",
            body_template="Details: {message}",
        )
        service.register_template(template)

        result = service.send_from_template(
            "alert",
            id="456",
            type="Error",
            message="Something went wrong",
        )
    """

    def __init__(self, router: NotificationRouter | None = None):
        self.router = router
        self._providers: dict[NotificationChannel, NotificationProvider] = {}
        self._templates: dict[str, NotificationTemplate] = {}
        self._history: list[NotificationResult] = []

    def register_provider(self, provider: NotificationProvider) -> None:
        """Register a notification provider."""
        self._providers[provider.channel] = provider

    def register_template(self, template: NotificationTemplate) -> None:
        """Register a notification template."""
        self._templates[template.name] = template

    def send(self, notification: Notification) -> NotificationResult:
        """Send a notification."""
        # Route if router configured
        channel = notification.channel
        if self.router:
            channel = self.router.route(notification)

        # Get provider
        provider = self._providers.get(channel)
        if not provider:
            result = NotificationResult(
                notification_id=notification.id,
                status=NotificationStatus.FAILED,
                channel=channel,
                error=f"No provider for channel: {channel.value}",
            )
            self._history.append(result)
            return result

        # Send
        result = provider.send(notification)
        self._history.append(result)
        return result

    def send_from_template(
        self,
        template_name: str,
        id: str,
        channel: NotificationChannel | None = None,
        priority: NotificationPriority | None = None,
        recipient: str | None = None,
        **variables,
    ) -> NotificationResult:
        """Send using a registered template."""
        template = self._templates.get(template_name)
        if not template:
            return NotificationResult(
                notification_id=id,
                status=NotificationStatus.FAILED,
                channel=NotificationChannel.CONSOLE,
                error=f"Template not found: {template_name}",
            )

        notification = template.render(
            id=id,
            channel=channel,
            priority=priority,
            recipient=recipient,
            **variables,
        )

        return self.send(notification)

    def broadcast(
        self,
        notification: Notification,
        channels: list[NotificationChannel],
    ) -> list[NotificationResult]:
        """Send to multiple channels."""
        results = []
        for channel in channels:
            n = Notification(
                id=f"{notification.id}_{channel.value}",
                subject=notification.subject,
                body=notification.body,
                channel=channel,
                priority=notification.priority,
                recipient=notification.recipient,
                metadata=notification.metadata,
            )
            results.append(self.send(n))
        return results

    @property
    def history(self) -> list[NotificationResult]:
        """Get notification history."""
        return self._history.copy()

    @property
    def success_count(self) -> int:
        """Get count of successful notifications."""
        return sum(1 for r in self._history if r.is_success)


# Common templates
ALERT_TEMPLATE = NotificationTemplate(
    name="alert",
    subject_template="[{severity}] {title}",
    body_template="Alert: {title}\n\nSeverity: {severity}\nSource: {source}\n\n{message}",
    default_priority=NotificationPriority.HIGH,
)

INFO_TEMPLATE = NotificationTemplate(
    name="info",
    subject_template="{title}",
    body_template="{message}",
    default_priority=NotificationPriority.LOW,
)

ERROR_TEMPLATE = NotificationTemplate(
    name="error",
    subject_template="Error: {title}",
    body_template="An error occurred:\n\nTitle: {title}\nDetails: {details}\n\nStack trace:\n{trace}",
    default_priority=NotificationPriority.CRITICAL,
)


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
