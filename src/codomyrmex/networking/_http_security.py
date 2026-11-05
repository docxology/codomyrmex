"""Connect-time public-address policy for the opt-in HTTP client mode.

Only this module's adapters enforce this policy. It does not constrain other
HTTP libraries, subprocesses, remote callback providers, or host routing.
"""

from __future__ import annotations

import ipaddress
import socket
import sys
from collections.abc import Mapping, Sequence
from typing import Any, Final, NoReturn
from urllib.parse import urlsplit

import requests
from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPConnection, HTTPSConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from urllib3.exceptions import ConnectTimeoutError, NewConnectionError
from urllib3.util import Timeout

SocketAddress = tuple[str, int] | tuple[str, int, int, int]
ResolvedAddress = tuple[int, int, int, str, SocketAddress]

# Translation/tunnel prefixes can embed a non-public IPv4 destination even
# when ipaddress considers the enclosing IPv6 address globally routable.
_TRANSITION_NETWORKS: Final = tuple(
    ipaddress.IPv6Network(prefix)
    for prefix in (
        "::/96",
        "::ffff:0:0/96",
        "64:ff9b::/96",
        "64:ff9b:1::/48",
        "2001::/32",
        "2002::/16",
    )
)


class PublicNetworkError(requests.exceptions.InvalidURL):
    """A request or resolved destination violates the public-only policy."""


def _require_public_ip(value: str) -> None:
    """Reject non-public and IPv6 translation/tunnel addresses."""
    if "%" in value:
        raise PublicNetworkError("Scoped IP addresses are not permitted")
    address = ipaddress.ip_address(value)
    if (
        not address.is_global
        or address.is_multicast
        or address.is_reserved
        or any(address in network for network in _TRANSITION_NETWORKS)
    ):
        raise PublicNetworkError("Destination must use a public IP address")


def _require_public_addresses(addresses: Sequence[ResolvedAddress]) -> None:
    """Validate the entire DNS answer before opening any socket."""
    if not addresses:
        raise PublicNetworkError("Destination has no resolved IP addresses")
    for family, _kind, _protocol, _canonical, sockaddr in addresses:
        if family not in (socket.AF_INET, socket.AF_INET6):
            raise PublicNetworkError("Destination has an unsupported address family")
        if len(sockaddr) == 4 and sockaddr[-1] != 0:
            raise PublicNetworkError("Scoped IP addresses are not permitted")
        _require_public_ip(sockaddr[0])


def _validate_request(request: requests.PreparedRequest) -> None:
    """Validate each prepared request, including redirected requests."""
    try:
        parsed = urlsplit(request.url or "")
        host = parsed.hostname
        # Accessing port also rejects malformed or out-of-range ports.
        _ = parsed.port
    except ValueError as exc:
        raise PublicNetworkError("Invalid HTTP destination URL") from exc
    if parsed.scheme not in ("http", "https") or not host:
        raise PublicNetworkError("Destination must be an absolute HTTP(S) URL")
    if parsed.username is not None or parsed.password is not None:
        raise PublicNetworkError("URL credentials are not permitted")
    if any(key.lower() == "host" for key in request.headers):
        raise PublicNetworkError("Host header overrides are not permitted")
    if "%" in host:
        raise PublicNetworkError("Scoped IP addresses are not permitted")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        # Hostname resolution is deliberately deferred to _new_conn, where
        # the actual socket is opened from the same validated DNS answer.
        return
    _require_public_ip(host)


def _public_socket(connection: HTTPConnection) -> socket.socket:
    """Resolve once and connect directly to one of those exact sockaddrs."""
    addresses = socket.getaddrinfo(
        connection._dns_host, connection.port, socket.AF_UNSPEC, socket.SOCK_STREAM
    )
    _require_public_addresses(addresses)
    last_error: OSError | None = None
    for family, kind, protocol, _canonical, sockaddr in addresses:
        sock: socket.socket | None = None
        try:
            sock = socket.socket(family, kind, protocol)
            for option in connection.socket_options or ():
                sock.setsockopt(*option)
            connect_timeout = connection.timeout
            if connect_timeout is Timeout.DEFAULT_TIMEOUT:
                connect_timeout = socket.getdefaulttimeout()
            sock.settimeout(connect_timeout)
            if connection.source_address:
                sock.bind(connection.source_address)
            # No create_connection(hostname) call here: it would resolve DNS
            # a second time and reopen the rebinding race.
            sock.connect(sockaddr)
        except OSError as exc:
            last_error = exc
            if sock is not None:
                sock.close()
        else:
            return sock
    if last_error is not None:
        raise last_error
    raise PublicNetworkError("Destination has no usable IP addresses")


def _new_public_connection(connection: HTTPConnection) -> socket.socket:
    """Preserve urllib3's retry/timeout exception contract."""
    try:
        sock = _public_socket(connection)
    except PublicNetworkError:
        raise
    except TimeoutError as exc:
        raise ConnectTimeoutError(
            connection, "Public HTTP connection timed out"
        ) from exc
    except OSError as exc:
        raise NewConnectionError(
            connection, "Public HTTP connection could not be established"
        ) from exc
    sys.audit("http.client.connect", connection, connection.host, connection.port)
    return sock


class _PublicHTTPConnection(HTTPConnection):
    def _new_conn(self) -> socket.socket:
        return _new_public_connection(self)


class _PublicHTTPSConnection(HTTPSConnection):
    def _new_conn(self) -> socket.socket:
        # Leave self.host unchanged for TLS SNI and certificate validation.
        return _new_public_connection(self)


class _PublicHTTPPool(HTTPConnectionPool):
    ConnectionCls = _PublicHTTPConnection


class _PublicHTTPSPool(HTTPSConnectionPool):
    ConnectionCls = _PublicHTTPSConnection


class PublicHTTPAdapter(HTTPAdapter):
    """Requests adapter enforcing public IPs for every fresh connection."""

    def init_poolmanager(
        self, connections: int, maxsize: int, block: bool = False, **pool_kwargs: Any
    ) -> None:
        # kwargs follow the third-party extension API, including TLS options.
        super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)
        # PoolManager's default mapping is shared; never mutate it globally.
        self.poolmanager.pool_classes_by_scheme = {
            **self.poolmanager.pool_classes_by_scheme,
            "http": _PublicHTTPPool,
            "https": _PublicHTTPSPool,
        }

    def proxy_manager_for(self, proxy: str, **proxy_kwargs: Any) -> NoReturn:
        raise PublicNetworkError("Proxies are not permitted in public-only mode")

    def send(
        self,
        request: requests.PreparedRequest,
        stream: bool = False,
        timeout: float | tuple[float | None, float | None] | Timeout | None = None,
        verify: bool | str = True,
        cert: str | tuple[str, str] | None = None,
        proxies: Mapping[str, str] | None = None,
    ) -> requests.Response:
        _validate_request(request)
        if proxies:
            raise PublicNetworkError("Proxies are not permitted in public-only mode")
        if not verify:
            raise PublicNetworkError("TLS verification is required in public-only mode")
        # requests dispatches redirects through Session.send again, invoking
        # this policy for each hop. urllib3 retries use the guarded pools.
        return super().send(
            request,
            stream=stream,
            timeout=timeout,
            verify=verify,
            cert=cert,
            proxies=proxies,
        )
