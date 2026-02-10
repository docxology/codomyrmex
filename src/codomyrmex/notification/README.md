# notification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Multi-channel notification system with templates and routing. Supports sending notifications across email, Slack, webhook, SMS, console, and file channels through pluggable provider backends. Includes a template engine for rendering parameterized notifications, a rule-based router for directing notifications to channels based on priority or custom conditions, and a central service that ties providers, templates, routing, and broadcast together with delivery history tracking.

## Installation

```bash
uv pip install codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Enums

- **`NotificationChannel`** -- Available channels: EMAIL, SLACK, WEBHOOK, SMS, CONSOLE, FILE
- **`NotificationPriority`** -- Priority levels: LOW, MEDIUM, HIGH, CRITICAL
- **`NotificationStatus`** -- Delivery statuses: PENDING, SENT, FAILED, DELIVERED

### Data Classes

- **`Notification`** -- A notification with ID, subject, body, channel, priority, optional recipient, and metadata; includes `to_dict()` serialization
- **`NotificationResult`** -- Result of sending a notification with status, channel, timestamp, optional error, and response payload; includes `is_success` property

### Providers

- **`NotificationProvider`** -- Abstract base class for channel providers with `channel` property and `send()` method
- **`ConsoleProvider`** -- Prints notifications to stdout with priority-based prefixes
- **`FileProvider`** -- Appends notifications as JSON lines to a log file
- **`WebhookProvider`** -- Sends notifications via HTTP webhook (mock implementation stores sent notifications for testing)

### Services

- **`NotificationTemplate`** -- Template for generating notifications from parameterized subject and body strings with default channel and priority; renders via `render()` with keyword variable substitution
- **`NotificationRouter`** -- Rule-based routing engine; evaluates condition functions against notifications to determine target channel; falls back to configurable default channel
- **`NotificationService`** -- Central notification service; registers providers and templates, sends notifications directly or from templates, supports multi-channel broadcast, and tracks delivery history with success counting

### Pre-built Templates

- **`ALERT_TEMPLATE`** -- Alert template with severity/title/source/message variables and HIGH default priority
- **`INFO_TEMPLATE`** -- Informational template with title/message variables and LOW default priority
- **`ERROR_TEMPLATE`** -- Error template with title/details/trace variables and CRITICAL default priority

## Directory Contents

- `models.py` -- Data models (Notification, NotificationResult, etc.)
- `providers.py` -- Channel providers (ConsoleProvider, FileProvider, etc.)
- `templates.py` -- Template engine (NotificationTemplate)
- `service.py` -- Core service and router (NotificationService, NotificationRouter)
- `__init__.py` -- Public API re-exports
- `README.md` -- This file
- `AGENTS.md` -- Agent integration documentation
- `API_SPECIFICATION.md` -- Programmatic API specification
- `MCP_TOOL_SPECIFICATION.md` -- Model Context Protocol tool definitions
- `PAI.md` -- PAI integration notes
- `SPEC.md` -- Module specification
- `py.typed` -- PEP 561 type stub marker as needed

## Quick Start

```python
from codomyrmex.notification import (
    NotificationService, ConsoleProvider, Notification,
    NotificationPriority, ALERT_TEMPLATE,
)

# Set up the notification service with a console provider
service = NotificationService()
service.register_provider(ConsoleProvider())

# Send a notification directly
result = service.send(Notification(
    id="n-001", subject="Build Complete", body="Deployment v2.1 succeeded",
    priority=NotificationPriority.HIGH,
))
print(f"Delivered: {result.is_success}")

# Send from a template
service.register_template("alert", ALERT_TEMPLATE)
service.send_from_template("alert", severity="WARN", title="CPU High", source="prod-1", message="CPU at 92%")
```

## Navigation

- **Full Documentation**: [docs/modules/notification/](../../../docs/modules/notification/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
