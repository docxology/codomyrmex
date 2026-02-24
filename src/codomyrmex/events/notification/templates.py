"""
Notification Templates

Template system for generating notifications.
"""

from .models import (
    Notification,
    NotificationChannel,
    NotificationPriority,
)


class NotificationTemplate:
    """
    Template for generating notifications.

    Usage:
        template = NotificationTemplate(
            name="alert",
            subject_template="Alert: {type} - {severity}",
            body_template="An alert was triggered:\\n\\nType: {type}\\nSeverity: {severity}\\nMessage: {message}",
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
        """Execute   Init   operations natively."""
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
