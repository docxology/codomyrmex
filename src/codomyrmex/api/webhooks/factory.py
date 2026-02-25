from .dispatcher import WebhookDispatcher
from .registry import WebhookRegistry
from .transport import HTTPWebhookTransport, WebhookTransport

# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------


def create_webhook_registry() -> WebhookRegistry:
    """Create a new, empty webhook registry.

    Returns:
        A fresh ``WebhookRegistry`` instance.
    """
    return WebhookRegistry()


def create_webhook_dispatcher(
    registry: WebhookRegistry | None = None,
    transport: WebhookTransport | None = None,
) -> WebhookDispatcher:
    """Create a webhook dispatcher with optional defaults.

    If no registry is provided, a new empty one is created. If no transport
    is provided, a default ``HTTPWebhookTransport`` with a no-op handler
    (always returns 200) is used.

    Args:
        registry: An existing ``WebhookRegistry`` to use (or ``None``).
        transport: An existing ``WebhookTransport`` to use (or ``None``).

    Returns:
        A configured ``WebhookDispatcher`` instance.
    """
    if registry is None:
        registry = create_webhook_registry()
    if transport is None:
        transport = HTTPWebhookTransport(
            handler=lambda url, payload, headers, timeout: (200, "OK")
        )
    return WebhookDispatcher(registry=registry, transport=transport)


