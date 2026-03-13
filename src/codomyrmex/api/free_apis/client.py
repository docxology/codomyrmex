"""HTTP client for calling discovered free APIs.

Uses only Python stdlib (``urllib.request``) so no extra dependencies
are required. Import ``httpx`` or ``requests`` in your own code for
advanced features (streaming, async, connection pooling).
"""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .models import APICallError, APICallResult

_DEFAULT_TIMEOUT = 10
_DEFAULT_METHOD = "GET"


# ---------------------------------------------------------------------------
# Module-level helpers (defined first so class can reference them inline)
# ---------------------------------------------------------------------------


def _append_params(url: str, params: dict[str, Any] | None) -> str:
    """Append query parameters to a URL string."""
    if not params:
        return url
    encoded = urllib.parse.urlencode({k: str(v) for k, v in params.items()})
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{encoded}"


def _encode_body(body: str | bytes | None) -> bytes | None:
    """Encode a request body to bytes."""
    if body is None:
        return None
    return body if isinstance(body, bytes) else body.encode("utf-8")


def _build_request(
    url: str,
    method: str,
    headers: dict[str, str],
    body: str | bytes | None,
) -> urllib.request.Request:
    """Construct a urllib Request with headers and encoded body."""
    data = _encode_body(body)
    req = urllib.request.Request(url, data=data, method=method.upper())
    for key, val in headers.items():
        req.add_header(key, val)
    return req


def _execute_request(
    req: urllib.request.Request,
    full_url: str,
    method: str,
    timeout: int,
) -> APICallResult:
    """Open the request and return an APICallResult; raise APICallError on failure."""
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return APICallResult(
                url=full_url,
                method=method.upper(),
                status_code=resp.status,
                headers=dict(resp.headers),
                body_text=resp.read().decode("utf-8", errors="replace"),
            )
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return APICallResult(
            url=full_url,
            method=method.upper(),
            status_code=exc.code,
            headers=dict(exc.headers) if exc.headers else {},
            body_text=body_text,
        )
    except urllib.error.URLError as exc:
        raise APICallError(f"Network error: {exc.reason}", url=full_url) from exc
    except TimeoutError as exc:
        raise APICallError(f"Request timed out after {timeout}s", url=full_url) from exc


# ---------------------------------------------------------------------------
# Public client class
# ---------------------------------------------------------------------------


class FreeAPIClient:
    """Thin HTTP client for calling public free APIs.

    Args:
        default_timeout: Request timeout in seconds. Default: 10.
        default_headers: Headers added to every request.
    """

    def __init__(
        self,
        default_timeout: int = _DEFAULT_TIMEOUT,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        self.default_timeout = default_timeout
        self.default_headers: dict[str, str] = default_headers or {
            "User-Agent": "codomyrmex/free_apis",
        }

    def call(
        self,
        url: str,
        method: str = _DEFAULT_METHOD,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        body: str | bytes | None = None,
        timeout: int | None = None,
    ) -> APICallResult:
        """Make an HTTP request to the given URL.

        Args:
            url: Full URL to request.
            method: HTTP verb. Default: ``"GET"``.
            headers: Additional request headers merged with defaults.
            params: Query parameters appended to the URL.
            body: Optional request body (bytes or str encoded as UTF-8).
            timeout: Per-request timeout override in seconds.

        Returns:
            :class:`~.models.APICallResult` with response data.

        Raises:
            :class:`~.models.APICallError`: On network errors or timeouts.
        """
        eff_timeout = timeout if timeout is not None else self.default_timeout
        full_url = _append_params(url, params)
        req = _build_request(full_url, method, {**self.default_headers, **(headers or {})}, body)
        return _execute_request(req, full_url, method, eff_timeout)

    def get(self, url: str, params: dict | None = None, timeout: int | None = None) -> APICallResult:
        """Convenience GET request."""
        return self.call(url, method="GET", params=params, timeout=timeout)

    def post(self, url: str, body: str | bytes | None = None, timeout: int | None = None) -> APICallResult:
        """Convenience POST request."""
        return self.call(url, method="POST", body=body, timeout=timeout)


__all__ = [
    "FreeAPIClient",
]
