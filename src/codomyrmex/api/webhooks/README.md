# Webhooks

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

Webhook dispatch and receipt management for event-driven APIs.

## Overview

The `webhooks` submodule provides a complete webhook system including event creation, webhook registration, payload signing/verification, and dispatching with retry support.

## Quick Start

```python
from codomyrmex.api.webhooks import (
    WebhookEventType, WebhookConfig, WebhookEvent,
    create_webhook_registry, create_webhook_dispatcher,
    HTTPWebhookTransport, WebhookSignature, SignatureAlgorithm,
)

# Create a registry and register a webhook
registry = create_webhook_registry()
registry.register("my-webhook", WebhookConfig(
    url="https://example.com/webhook",
    secret="my-secret-key",
    events=[WebhookEventType.CREATED, WebhookEventType.UPDATED],
    max_retries=3,
    retry_delay=1.0,
))

# Create a dispatcher with a custom transport
def my_handler(url, payload, headers, timeout):
    # Your HTTP logic here
    return (200, "OK")

transport = HTTPWebhookTransport(handler=my_handler)
dispatcher = create_webhook_dispatcher(registry=registry, transport=transport)

# Dispatch an event
event = WebhookEvent(
    event_type=WebhookEventType.CREATED,
    payload={"user_id": "123", "action": "signup"},
    source="user-service",
)
results = dispatcher.dispatch(event)

# Or dispatch with automatic retries
results = dispatcher.dispatch_with_retry(event, max_retries=5)

# Sign and verify payloads manually
signature = WebhookSignature.sign("payload", "secret", SignatureAlgorithm.HMAC_SHA256)
is_valid = WebhookSignature.verify("payload", "secret", signature, SignatureAlgorithm.HMAC_SHA256)
```

## Features

- Event-driven webhook dispatch with configurable event types
- HMAC-SHA256/SHA512 payload signing and verification
- Webhook registry with event-type filtering
- Automatic retry with configurable delay
- Pluggable transport layer (callback-based for testing)
- Factory functions for quick setup

## API Reference

See [API_SPECIFICATION.md](./API_SPECIFICATION.md) for detailed API documentation.

## Related Modules

- [`api`](../) - Parent module
- [`api.authentication`](../authentication/) - Authentication mechanisms
