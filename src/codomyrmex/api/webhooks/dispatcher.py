import time

from .models import DeliveryResult, WebhookConfig, WebhookEvent, WebhookStatus
from .registry import WebhookRegistry
from .signature import WebhookSignature
from .transport import WebhookTransport


class WebhookDispatcher:
    """Dispatches webhook events to registered endpoints via a transport.

    Coordinates between the ``WebhookRegistry`` (which webhooks to target),
    the ``WebhookSignature`` class (payload signing), and a
    ``WebhookTransport`` (actual delivery).

    Args:
        registry: The registry to look up webhooks from.
        transport: The transport used to deliver payloads.
    """

    def __init__(
        self,
        registry: WebhookRegistry,
        transport: WebhookTransport,
    ) -> None:
        self._registry = registry
        self._transport = transport

    @property
    def registry(self) -> WebhookRegistry:
        """Access the underlying webhook registry."""
        return self._registry

    @property
    def transport(self) -> WebhookTransport:
        """Access the underlying transport."""
        return self._transport

    def _build_headers(
        self,
        event: WebhookEvent,
        config: WebhookConfig,
        payload_json: str,
    ) -> dict[str, str]:
        """Build HTTP headers including the HMAC signature.

        Args:
            event: The event being dispatched.
            config: The webhook configuration (contains secret/algorithm).
            payload_json: The serialized JSON payload string.

        Returns:
            Dictionary of header name to header value.
        """
        signature = WebhookSignature.sign(
            payload_json, config.secret, config.signature_algorithm
        )
        return {
            "Content-Type": "application/json",
            "X-Webhook-Event": event.event_type.value,
            "X-Webhook-Event-Id": event.event_id,
            "X-Webhook-Signature": signature,
            "X-Webhook-Signature-Algorithm": config.signature_algorithm.value,
            "X-Webhook-Timestamp": event.timestamp.isoformat(),
        }

    def _deliver(
        self,
        webhook_id: str,
        event: WebhookEvent,
        config: WebhookConfig,
        attempt: int = 1,
    ) -> DeliveryResult:
        """Attempt a single delivery of an event to a webhook endpoint.

        Args:
            webhook_id: Identifier of the target webhook.
            event: The event to deliver.
            config: Configuration of the target webhook.
            attempt: The attempt number (1-based).

        Returns:
            A ``DeliveryResult`` describing the outcome.
        """
        payload_json = event.to_json()
        headers = self._build_headers(event, config, payload_json)

        try:
            status_code, _body = self._transport.send(
                url=config.url,
                payload=payload_json,
                headers=headers,
                timeout=config.timeout,
            )

            if 200 <= status_code < 300:
                return DeliveryResult(
                    webhook_id=webhook_id,
                    event_id=event.event_id,
                    status=WebhookStatus.DELIVERED,
                    status_code=status_code,
                    attempt=attempt,
                )
            else:
                return DeliveryResult(
                    webhook_id=webhook_id,
                    event_id=event.event_id,
                    status=WebhookStatus.FAILED,
                    status_code=status_code,
                    attempt=attempt,
                    error=f"Non-success status code: {status_code}",
                )
        except Exception as exc:
            return DeliveryResult(
                webhook_id=webhook_id,
                event_id=event.event_id,
                status=WebhookStatus.FAILED,
                attempt=attempt,
                error=str(exc),
            )

    def dispatch(self, event: WebhookEvent) -> list[DeliveryResult]:
        """Dispatch an event to all matching registered webhooks.

        Iterates over all active webhooks subscribed to the event type,
        signs the payload, sends via transport, and collects results.

        Args:
            event: The webhook event to dispatch.

        Returns:
            List of ``DeliveryResult`` objects, one per targeted webhook.
        """
        targets = self._registry.list_for_event(event.event_type)
        results: list[DeliveryResult] = []

        for webhook_id, config in targets.items():
            result = self._deliver(webhook_id, event, config, attempt=1)
            results.append(result)

        return results

    def dispatch_with_retry(
        self,
        event: WebhookEvent,
        max_retries: int | None = None,
    ) -> list[DeliveryResult]:
        """Dispatch an event with automatic retries on failure.

        For each targeted webhook, if the initial delivery fails, retries
        up to ``max_retries`` times (defaulting to the webhook's own
        ``max_retries`` config value). A simple linear back-off based on
        the webhook's ``retry_delay`` is applied between attempts.

        Args:
            event: The webhook event to dispatch.
            max_retries: Override for the per-webhook max_retries setting.
                If ``None``, each webhook's own ``max_retries`` is used.

        Returns:
            List of final ``DeliveryResult`` objects, one per targeted
            webhook. Each result reflects the outcome of the last attempt
            (whether successful or the final failure).
        """
        targets = self._registry.list_for_event(event.event_type)
        results: list[DeliveryResult] = []

        for webhook_id, config in targets.items():
            retries = max_retries if max_retries is not None else config.max_retries
            last_result: DeliveryResult | None = None

            for attempt in range(1, retries + 2):  # attempts = retries + 1
                result = self._deliver(
                    webhook_id, event, config, attempt=attempt
                )

                if result.status == WebhookStatus.DELIVERED:
                    last_result = result
                    break

                # Mark as retrying if we have more attempts left
                if attempt <= retries:
                    result.status = WebhookStatus.RETRYING
                    time.sleep(config.retry_delay)

                last_result = result

            if last_result is not None:
                results.append(last_result)

        return results


