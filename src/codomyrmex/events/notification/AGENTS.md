# Codomyrmex Agents — src/codomyrmex/events/notification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides a multi-channel notification system with pluggable providers, template-based message rendering, rule-based routing, and broadcasting. Supports console, file, and webhook delivery channels out of the box.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `NotificationChannel` | Enum: EMAIL, SLACK, WEBHOOK, SMS, CONSOLE, FILE |
| `models.py` | `NotificationPriority` | Enum: LOW, MEDIUM, HIGH, CRITICAL |
| `models.py` | `NotificationStatus` | Enum: PENDING, SENT, FAILED, DELIVERED |
| `models.py` | `Notification` | Dataclass with id, subject, body, channel, priority, recipient, metadata, created_at; provides `to_dict()` |
| `models.py` | `NotificationResult` | Dataclass capturing delivery outcome: status, channel, sent_at, error, response; `is_success` property |
| `providers.py` | `NotificationProvider` | ABC with abstract `channel` property and `send(notification)` method |
| `providers.py` | `ConsoleProvider` | Prints notifications to stdout with priority-based prefix symbols |
| `providers.py` | `FileProvider` | Appends JSON-serialized notifications to a log file |
| `providers.py` | `WebhookProvider` | Sends notifications to a configured URL (stores in `_sent` list for testing) |
| `templates.py` | `NotificationTemplate` | Renders notifications from subject/body format strings with variable substitution |
| `templates.py` | `ALERT_TEMPLATE` / `INFO_TEMPLATE` / `ERROR_TEMPLATE` | Pre-built templates for common notification types |
| `service.py` | `NotificationRouter` | Rule-based router: evaluates condition callables to select delivery channel, with a configurable default |
| `service.py` | `NotificationService` | Central service: registers providers and templates, sends single or broadcast notifications, maintains delivery history |

## Operating Contracts

- `NotificationService.send()` returns `NotificationResult` with `FAILED` status and error message if no provider is registered for the target channel -- no exception raised.
- `NotificationRouter.add_rule()` and `add_default()` return `self` for method chaining.
- `FileProvider.send()` catches all standard exceptions and returns a `FAILED` result rather than propagating.
- `NotificationService.broadcast()` clones the notification with a channel-specific ID suffix for each target channel.
- `NotificationTemplate.render()` uses Python `str.format()` for variable interpolation; missing variables raise `KeyError`.
- `cli_commands()` returns a dict suitable for CLI integration (channels listing and console-based send).

## Integration Points

- **Depends on**: Standard library only (no cross-module imports except optional `codomyrmex.validation.schemas`)
- **Used by**: Alert systems, monitoring dashboards, and any module that needs to send structured notifications

## Navigation

- **Parent**: [events](../README.md)
- **Root**: [Codomyrmex](../../../../../README.md)
