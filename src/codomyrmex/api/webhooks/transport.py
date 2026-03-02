from abc import ABC, abstractmethod
from collections.abc import Callable

# Abstract base class
# ---------------------------------------------------------------------------


class WebhookTransport(ABC):
    """Abstract transport layer for sending webhook payloads.

    Implementations must provide a ``send`` method that delivers a payload
    to a target URL and returns the HTTP status code and response body.
    """

    @abstractmethod
    def send(
        self,
        url: str,
        payload: str,
        headers: dict[str, str],
        timeout: float,
    ) -> tuple[int, str]:
        """Send a webhook payload to the given URL.

        Args:
            url: Target endpoint URL.
            payload: Serialized payload body (JSON string).
            headers: HTTP headers to include with the request.
            timeout: Request timeout in seconds.

        Returns:
            A tuple of (status_code, response_body).
        """
        pass


# ---------------------------------------------------------------------------
# Concrete classes
# ---------------------------------------------------------------------------


class HTTPWebhookTransport(WebhookTransport):
    """Callback-based webhook transport for testing and in-process dispatch.

    Instead of making real HTTP requests this transport delegates delivery
    to a user-supplied callable, making it ideal for unit tests and
    local event buses.

    Args:
        handler: A callable that receives ``(url, payload, headers, timeout)``
            and returns a tuple of ``(status_code, response_body)``.
    """

    def __init__(
        self,
        handler: Callable[
            [str, str, dict[str, str], float], tuple[int, str]
        ],
    ) -> None:
        self._handler = handler

    def send(
        self,
        url: str,
        payload: str,
        headers: dict[str, str],
        timeout: float,
    ) -> tuple[int, str]:
        """Delegate delivery to the configured handler callable.

        Args:
            url: Target endpoint URL.
            payload: Serialized payload body (JSON string).
            headers: HTTP headers to include with the request.
            timeout: Request timeout in seconds.

        Returns:
            A tuple of (status_code, response_body) as returned by the handler.
        """
        return self._handler(url, payload, headers, timeout)


