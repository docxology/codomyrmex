# Events Notification — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Multi-channel notification system with a provider abstraction layer, template-based rendering, rule-based routing, and multi-channel broadcasting. Ships with console, file, and webhook providers.

## Architecture

Strategy pattern for delivery (`NotificationProvider` ABC with channel-specific implementations). Chain-of-responsibility for routing (`NotificationRouter` evaluates rules in order). Template pattern for message composition (`NotificationTemplate` with `str.format()` interpolation). `NotificationService` orchestrates all three.

## Key Classes

### `Notification`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique notification identifier |
| `subject` | `str` | Notification subject line |
| `body` | `str` | Notification body text |
| `channel` | `NotificationChannel` | Delivery channel (default: CONSOLE) |
| `priority` | `NotificationPriority` | Priority level (default: MEDIUM) |
| `recipient` | `str \| None` | Optional recipient identifier |
| `metadata` | `dict[str, Any]` | Arbitrary metadata |
| `created_at` | `datetime` | Creation timestamp |

### `NotificationProvider` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `channel` | — (property) | `NotificationChannel` | The channel this provider handles |
| `send` | `notification: Notification` | `NotificationResult` | Deliver a notification |

### `NotificationService`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `router: NotificationRouter \| None` | `None` | Initialize with optional router |
| `register_provider` | `provider: NotificationProvider` | `None` | Register a delivery provider |
| `register_template` | `template: NotificationTemplate` | `None` | Register a named template |
| `send` | `notification: Notification` | `NotificationResult` | Route and deliver a notification |
| `send_from_template` | `template_name`, `id`, `channel`, `priority`, `recipient`, `**variables` | `NotificationResult` | Render template and send |
| `broadcast` | `notification`, `channels: list[NotificationChannel]` | `list[NotificationResult]` | Send to multiple channels |
| `history` | — (property) | `list[NotificationResult]` | Copy of delivery history |
| `success_count` | — (property) | `int` | Count of successful deliveries |

### `NotificationRouter`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_rule` | `condition: Callable[[Notification], bool]`, `channel` | `self` | Add routing rule (chainable) |
| `add_default` | `channel: NotificationChannel` | `self` | Set fallback channel (chainable) |
| `route` | `notification: Notification` | `NotificationChannel` | Evaluate rules and return target channel |

### `NotificationTemplate`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `name`, `subject_template`, `body_template`, `default_channel`, `default_priority` | `None` | Define template with format strings |
| `render` | `id`, `channel`, `priority`, `recipient`, `**variables` | `Notification` | Interpolate variables and return notification |

## Dependencies

- **Internal**: Optional import of `codomyrmex.validation.schemas` (for cross-module interop)
- **External**: Standard library only (`json`, `abc`, `datetime`)

## Constraints

- `NotificationRouter` evaluates rules in insertion order; first match wins.
- `NotificationService.broadcast()` creates cloned notifications with `{id}_{channel.value}` suffixed IDs.
- `FileProvider` appends one JSON line per notification; the file is not truncated.
- `WebhookProvider.send()` stores notifications in `_sent` list but does not perform real HTTP requests (placeholder for real implementation).
- Pre-built templates: `ALERT_TEMPLATE` (HIGH priority), `INFO_TEMPLATE` (LOW), `ERROR_TEMPLATE` (CRITICAL).
- `NotificationResult.is_success` returns `True` for both SENT and DELIVERED statuses.

## Error Handling

- `FileProvider.send()` catches all standard exceptions and returns a `FAILED` result with the error message.
- `NotificationService.send()` returns `FAILED` result with descriptive error when no provider is registered for the target channel.
- `NotificationService.send_from_template()` returns `FAILED` result when the template name is not found.
- `NotificationTemplate.render()` raises `KeyError` if required variables are missing from `**variables`.
