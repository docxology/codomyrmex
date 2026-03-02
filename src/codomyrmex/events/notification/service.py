"""
Notification Service

Central notification service with routing and broadcasting.
"""

from collections.abc import Callable

from .models import (
    Notification,
    NotificationChannel,
    NotificationPriority,
    NotificationResult,
    NotificationStatus,
)
from .providers import NotificationProvider
from .templates import NotificationTemplate


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
        """Initialize this instance."""
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
        """Initialize this instance."""
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
