# Notification Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Multi-channel notification system with templates, routing, and provider-based dispatch. Supports sending notifications through console, file, webhook, email, Slack, and SMS channels. Features a template engine for rendering notifications from parameterized templates, a rule-based router for directing notifications to appropriate channels based on priority or custom conditions, and a central service that ties providers, templates, and routing together with broadcast and history tracking capabilities.

## Key Features

- **Multi-Channel Dispatch**: Send notifications through console, file, webhook, email, Slack, and SMS channels via pluggable providers
- **Template Engine**: Define reusable notification templates with parameterized subjects and bodies using Python string formatting
- **Rule-Based Routing**: Route notifications to channels dynamically based on priority, content, or custom conditions
- **Broadcast Support**: Send a single notification to multiple channels simultaneously
- **Notification History**: Track all sent notification results with success/failure status and error details
- **Built-in Templates**: Pre-configured templates for alerts (`ALERT_TEMPLATE`), informational messages (`INFO_TEMPLATE`), and errors (`ERROR_TEMPLATE`)
- **Priority Levels**: Four priority tiers (LOW, MEDIUM, HIGH, CRITICAL) for notification classification
- **Provider Architecture**: Abstract `NotificationProvider` base class for implementing custom channel providers

## Key Components

| Component | Description |
|-----------|-------------|
| `NotificationService` | Central service coordinating providers, templates, routing, broadcast, and history tracking |
| `NotificationRouter` | Rule-based router that directs notifications to channels based on configurable conditions |
| `NotificationTemplate` | Template engine for rendering notifications from parameterized subject and body strings |
| `Notification` | Core notification dataclass with id, subject, body, channel, priority, and recipient |
| `NotificationResult` | Result of sending a notification including status, timestamps, and error details |
| `NotificationProvider` | Abstract base class for implementing channel-specific notification providers |
| `ConsoleProvider` | Provider that prints notifications to the console with priority-based formatting |
| `FileProvider` | Provider that appends notifications as JSON to a log file |
| `WebhookProvider` | Provider that sends notifications via HTTP webhook (mock implementation for testing) |
| `NotificationChannel` | Enum of channels: EMAIL, SLACK, WEBHOOK, SMS, CONSOLE, FILE |
| `NotificationPriority` | Enum of priority levels: LOW, MEDIUM, HIGH, CRITICAL |
| `NotificationStatus` | Enum of statuses: PENDING, SENT, FAILED, DELIVERED |
| `ALERT_TEMPLATE` | Pre-built template for alert notifications with severity and source fields |
| `INFO_TEMPLATE` | Pre-built template for informational notifications |
| `ERROR_TEMPLATE` | Pre-built template for error notifications with title, details, and stack trace fields |

## Quick Start

```python
from codomyrmex.notification import (
    NotificationService, ConsoleProvider, Notification, NotificationPriority
)

# Set up the service with a console provider
service = NotificationService()
service.register_provider(ConsoleProvider())

# Send a notification
result = service.send(Notification(
    id="notif_001",
    subject="Build Complete",
    body="All tests passed successfully.",
    priority=NotificationPriority.MEDIUM,
))
print(result.is_success)  # True
```

```python
from codomyrmex.notification import (
    NotificationService, ConsoleProvider, FileProvider,
    NotificationTemplate, NotificationChannel, NotificationPriority,
)

# Set up service with multiple providers
service = NotificationService()
service.register_provider(ConsoleProvider())
service.register_provider(FileProvider("notifications.log"))

# Register a custom template
template = NotificationTemplate(
    name="deploy",
    subject_template="Deployment: {env} - {status}",
    body_template="Service {service} deployed to {env}.\nStatus: {status}",
    default_priority=NotificationPriority.HIGH,
)
service.register_template(template)

# Send from template
result = service.send_from_template(
    "deploy",
    id="deploy_42",
    env="production",
    status="success",
    service="api-gateway",
)
```

```python
from codomyrmex.notification import (
    NotificationService, ConsoleProvider, WebhookProvider,
    NotificationRouter, NotificationPriority, NotificationChannel,
    Notification,
)

# Set up routing: critical goes to webhook, rest to console
router = NotificationRouter()
router.add_rule(
    lambda n: n.priority == NotificationPriority.CRITICAL,
    NotificationChannel.WEBHOOK,
)
router.add_default(NotificationChannel.CONSOLE)

service = NotificationService(router=router)
service.register_provider(ConsoleProvider())
service.register_provider(WebhookProvider("https://hooks.example.com/alerts"))

# Critical notification auto-routes to webhook
service.send(Notification(
    id="critical_001",
    subject="Database Down",
    body="Primary database is unreachable.",
    priority=NotificationPriority.CRITICAL,
))
```

## Related Modules

- [observability_dashboard](../observability_dashboard/) - Alert management that may trigger notifications
- [logging_monitoring](../logging_monitoring/) - Centralized logging that complements notification dispatch

## Navigation

- **Source**: [src/codomyrmex/notification/](../../../src/codomyrmex/notification/)
- **Parent**: [docs/modules/](../README.md)
