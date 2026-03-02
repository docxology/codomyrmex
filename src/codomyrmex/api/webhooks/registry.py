from .models import WebhookConfig, WebhookEventType


class WebhookRegistry:
    """In-memory registry for webhook configurations.

    Stores webhook configs keyed by a string identifier and provides
    lookup, listing, and filtering capabilities.
    """

    def __init__(self) -> None:
        self._webhooks: dict[str, WebhookConfig] = {}

    def register(self, webhook_id: str, config: WebhookConfig) -> None:
        """Register a new webhook or update an existing one.

        Args:
            webhook_id: Unique identifier for the webhook.
            config: The webhook configuration to store.
        """
        self._webhooks[webhook_id] = config

    def unregister(self, webhook_id: str) -> None:
        """Remove a webhook from the registry.

        Args:
            webhook_id: Identifier of the webhook to remove.

        Raises:
            KeyError: If the webhook_id is not found.
        """
        if webhook_id not in self._webhooks:
            raise KeyError(f"Webhook '{webhook_id}' not found in registry")
        del self._webhooks[webhook_id]

    def get(self, webhook_id: str) -> WebhookConfig | None:
        """Retrieve a webhook config by identifier.

        Args:
            webhook_id: Identifier of the webhook.

        Returns:
            The ``WebhookConfig`` if found, otherwise ``None``.
        """
        return self._webhooks.get(webhook_id)

    def list_all(self) -> dict[str, WebhookConfig]:
        """Return a copy of all registered webhooks.

        Returns:
            Dictionary mapping webhook IDs to their configs.
        """
        return dict(self._webhooks)

    def list_for_event(
        self, event_type: WebhookEventType
    ) -> dict[str, WebhookConfig]:
        """Return all active webhooks subscribed to a given event type.

        A webhook matches if it is active **and** either has the event type
        in its ``events`` list or has an empty ``events`` list (subscribes
        to all events).

        Args:
            event_type: The event type to filter by.

        Returns:
            Dictionary of matching webhook IDs to their configs.
        """
        return {
            wid: config
            for wid, config in self._webhooks.items()
            if config.active
            and (event_type in config.events or len(config.events) == 0)
        }


