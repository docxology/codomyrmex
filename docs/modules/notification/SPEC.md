# Notification — Functional Specification

**Module**: `codomyrmex.notification`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Multi-channel notification system with templates and routing.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `NotificationChannel` | Class | Available notification channels. |
| `NotificationPriority` | Class | Priority levels for notifications. |
| `NotificationStatus` | Class | Status of a notification. |
| `Notification` | Class | A notification to be sent. |
| `NotificationResult` | Class | Result of sending a notification. |
| `NotificationProvider` | Class | Base class for notification providers. |
| `ConsoleProvider` | Class | Print notifications to console. |
| `FileProvider` | Class | Write notifications to a file. |
| `WebhookProvider` | Class | Send notifications via webhook (mock for testing). |
| `NotificationTemplate` | Class |     Template for generating notifications. |
| `to_dict()` | Function | Convert to dictionary. |
| `is_success()` | Function | is success |
| `channel()` | Function | Get the channel this provider handles. |
| `send()` | Function | Send a notification. |
| `channel()` | Function | channel |

## 3. Dependencies

See `src/codomyrmex/notification/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.notification import NotificationChannel, NotificationPriority, NotificationStatus, Notification, NotificationResult
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k notification -v
```
