"""Webhook management mixin for AgentMailProvider.

Provides webhook operations: list, get, create, update, and delete webhooks.
"""

from __future__ import annotations

from typing import Any

from ...exceptions import EmailAPIError
from ..models import (
    AgentMailWebhook,
    _sdk_webhook_to_model,
)

try:
    from agentmail.core import ApiError
except ImportError:
    ApiError = Exception  # type: ignore


def _raise_for_api_error(exc: Exception, context: str):
    """Import and delegate to the module-level error raiser."""
    from ..provider import _raise_for_api_error as _raise
    _raise(exc, context)


class WebhookMixin:
    """Mixin providing webhook management methods for AgentMailProvider."""

    def list_webhooks(self, limit: int = 50) -> list[AgentMailWebhook]:
        """List all webhook subscriptions.

        Args:
            limit: Maximum number of webhooks to return.

        Returns:
            List of AgentMailWebhook objects.
        """
        try:
            response = self._client.webhooks.list(limit=limit)
            items = getattr(response, "webhooks", None) or list(response)
            return [_sdk_webhook_to_model(w) for w in items]
        except ApiError as exc:
            _raise_for_api_error(exc, "list_webhooks")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error listing webhooks: {exc}") from exc

    def get_webhook(self, webhook_id: str) -> AgentMailWebhook:
        """Fetch a specific webhook.

        Args:
            webhook_id: The webhook ID.

        Returns:
            AgentMailWebhook object.

        Raises:
            MessageNotFoundError: If the webhook does not exist.
        """
        try:
            webhook = self._client.webhooks.get(webhook_id)
            return _sdk_webhook_to_model(webhook)
        except ApiError as exc:
            _raise_for_api_error(exc, f"get_webhook({webhook_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error fetching webhook {webhook_id}: {exc}") from exc

    def create_webhook(
        self,
        url: str,
        event_types: list[str],
        inbox_ids: list[str] | None = None,
        pod_ids: list[str] | None = None,
    ) -> AgentMailWebhook:
        """Register a new webhook subscription.

        Args:
            url: The HTTPS endpoint to receive events.
            event_types: List of event types (e.g., ``["message.received"]``).
            inbox_ids: Restrict events to specific inboxes.
            pod_ids: Restrict events to specific pods.

        Returns:
            The registered AgentMailWebhook.
        """
        try:
            kwargs: dict[str, Any] = {"url": url, "event_types": event_types}
            if inbox_ids:
                kwargs["inbox_ids"] = inbox_ids
            if pod_ids:
                kwargs["pod_ids"] = pod_ids
            webhook = self._client.webhooks.create(**kwargs)
            return _sdk_webhook_to_model(webhook)
        except ApiError as exc:
            _raise_for_api_error(exc, "create_webhook")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error creating webhook: {exc}") from exc

    def update_webhook(
        self,
        webhook_id: str,
        add_inbox_ids: list[str] | None = None,
        remove_inbox_ids: list[str] | None = None,
    ) -> AgentMailWebhook:
        """Update a webhook's inbox subscriptions.

        Args:
            webhook_id: The webhook ID to update.
            add_inbox_ids: Inboxes to add to the subscription.
            remove_inbox_ids: Inboxes to remove from the subscription.

        Returns:
            Updated AgentMailWebhook.
        """
        try:
            kwargs: dict[str, Any] = {}
            if add_inbox_ids:
                kwargs["add_inbox_ids"] = add_inbox_ids
            if remove_inbox_ids:
                kwargs["remove_inbox_ids"] = remove_inbox_ids
            webhook = self._client.webhooks.update(webhook_id, **kwargs)
            return _sdk_webhook_to_model(webhook)
        except ApiError as exc:
            _raise_for_api_error(exc, f"update_webhook({webhook_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error updating webhook {webhook_id}: {exc}") from exc

    def delete_webhook(self, webhook_id: str) -> None:
        """Delete a webhook subscription.

        Args:
            webhook_id: The webhook ID to delete.

        Raises:
            MessageNotFoundError: If the webhook does not exist.
        """
        try:
            self._client.webhooks.delete(webhook_id)
        except ApiError as exc:
            _raise_for_api_error(exc, f"delete_webhook({webhook_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error deleting webhook {webhook_id}: {exc}") from exc
