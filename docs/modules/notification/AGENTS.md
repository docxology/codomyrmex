# Notification Module — Agent Coordination

## Purpose

Multi-channel notification system with templates and routing.

## Key Capabilities

- **NotificationChannel**: Available notification channels.
- **NotificationPriority**: Priority levels for notifications.
- **NotificationStatus**: Status of a notification.
- **Notification**: A notification to be sent.
- **NotificationResult**: Result of sending a notification.
- `to_dict()`: Convert to dictionary.
- `is_success()`: is success
- `channel()`: Get the channel this provider handles.

## Agent Usage Patterns

```python
from codomyrmex.notification import NotificationChannel

# Agent initializes notification
instance = NotificationChannel()
```

## Integration Points

- **Source**: [src/codomyrmex/notification/](../../../src/codomyrmex/notification/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)
