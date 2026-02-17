"""
Notification Models

Data classes and enums for the notification system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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
