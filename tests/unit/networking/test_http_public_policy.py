"""Public-only HTTP controls using real requests, DNS, and local servers.

Address classification uses explicit DNS-answer data. No external services,
credentials, patched networking functions, or import-time probes are used.
"""

from __future__ import annotations

import queue
import socket
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
import requests
from requests.adapters import HTTPAdapter

from codomyrmex.networking._http_security import (
    PublicNetworkError,
    ResolvedAddress,
    _PublicHTTPConnection,
    _PublicHTTPSConnection,
    _require_public_addresses,
    _require_public_ip,
    _validate_request,
)
from codomyrmex.networking.http_client import HTTPClient, NetworkingError


@pytest.fixture
def local_http() -> Iterator[tuple[str, queue.Queue[str]]]:
    received: queue.Queue[str] = queue.Queue()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            received.put(self.path)
            if self.path == "/redirect":
                self.send_response(302)
                self.send_header(
                    "Location", f"http://localhost:{server.server_port}/blocked"
                )
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, format: str, *args: str) -> None:
            return

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}", received
        finally:
            server.shutdown()
            thread.join(timeout=2)


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",
        "10.0.0.1",
        "172.16.0.1",
        "192.168.1.1",
        "169.254.169.254",
        "100.100.100.200",
        "0.0.0.0",
        "224.0.0.1",
        "240.0.0.1",
        "192.0.2.1",
        "::",
        "::1",
        "fc00::1",
        "fe80::1",
        "fe80::1%en0",
        "ff02::1",
        "2001:db8::1",
        "::ffff:127.0.0.1",
        "::ffff:8.8.8.8",
        "64:ff9b::a9fe:a9fe",
        "64:ff9b:1::7f00:1",
        "2002:7f00:1::",
        "2001:0:4136:e378:8000:63bf:3fff:fdd2",
    ],
)
def test_public_ip_policy_rejects_nonpublic_or_translated_addresses(
    address: str,
) -> None:
    # Given an explicit address; when classifying it; then refuse it.
    with pytest.raises(PublicNetworkError):
        _require_public_ip(address)


@pytest.mark.parametrize("address", ["8.8.8.8", "1.1.1.1", "2606:4700:4700::1111"])
def test_public_ip_policy_accepts_public_unicast(address: str) -> None:
    # Given a public unicast address; when classifying it; then accept it.
    _require_public_ip(address)


@pytest.mark.parametrize("private_first", [True, False])
def test_mixed_dns_answers_are_rejected_in_either_order(private_first: bool) -> None:
    # Given both a public and local DNS answer, regardless of answer order.
    addresses: list[ResolvedAddress] = [
        (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("8.8.8.8", 80)),
        (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("127.0.0.1", 80)),
    ]
    if private_first:
        addresses.reverse()
    # When validating the whole answer; then no partial answer is accepted.
    with pytest.raises(PublicNetworkError):
        _require_public_addresses(addresses)


def test_empty_dns_answer_is_rejected() -> None:
    # Given no answers; when validating them; then refuse the destination.
    with pytest.raises(PublicNetworkError):
        _require_public_addresses([])


def test_all_public_ipv4_and_ipv6_dns_answers_are_accepted() -> None:
    # Given a complete public dual-stack DNS answer.
    addresses: list[ResolvedAddress] = [
        (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("8.8.8.8", 443)),
        (
            socket.AF_INET6,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP,
            "",
            ("2606:4700:4700::1111", 443, 0, 0),
        ),
    ]
    # When validating the complete answer; then admit it without a connection.
    _require_public_addresses(addresses)


def test_ipv6_scope_id_in_sockaddr_is_rejected() -> None:
    # Given a global IPv6 address carrying an explicit socket scope identifier.
    addresses: list[ResolvedAddress] = [
        (
            socket.AF_INET6,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP,
            "",
            ("2606:4700:4700::1111", 443, 0, 1),
        ),
    ]
    # When validating the answer; then reject even without a percent-suffixed IP.
    with pytest.raises(PublicNetworkError):
        _require_public_addresses(addresses)


@pytest.mark.parametrize(
    "connection_type", [_PublicHTTPConnection, _PublicHTTPSConnection]
)
def test_both_connection_schemes_reject_real_localhost_dns(
    connection_type: type[_PublicHTTPConnection | _PublicHTTPSConnection],
) -> None:
    # Given the real system localhost resolver and each guarded connection.
    connection = connection_type("localhost", port=1, timeout=0.1)
    # When opening a socket; then reject DNS answers before TCP/TLS.
    with pytest.raises(PublicNetworkError):
        connection._new_conn()


@pytest.mark.parametrize(
    ("url", "headers"),
    [
        ("https://user:password@8.8.8.8/", {}),  # pragma: allowlist secret
        ("http://8.8.8.8/", {"hOsT": "internal.example"}),
        ("http://127.0.0.1/", {}),
        ("http://[::ffff:127.0.0.1]/", {}),
        ("ftp://8.8.8.8/file", {}),
    ],
)
def test_prepared_requests_cannot_override_the_destination(
    url: str, headers: dict[str, str]
) -> None:
    # Given a real prepared request, including a redirected request shape.
    request = requests.Request("GET", url, headers=headers).prepare()
    # When applying the per-send policy; then refuse dangerous inputs.
    with pytest.raises(PublicNetworkError):
        _validate_request(request)


def test_default_client_preserves_local_service_access(
    local_http: tuple[str, queue.Queue[str]],
) -> None:
    # Given the legacy client and a real loopback server.
    url, received = local_http
    protected = HTTPClient(public_only=True)
    client = HTTPClient(max_retries=0)
    client.session.trust_env = False
    try:
        # When requesting local content; then retain ordinary HTTP behavior.
        response = client.get(url + "/legacy")
        assert response.text == "ok"
        assert received.get_nowait() == "/legacy"
    finally:
        client.session.close()
        protected.session.close()


@pytest.mark.parametrize(
    "host",
    ["127.0.0.1", "localhost", "127.1", "2130706433", "0x7f000001", "0177.0.0.1"],
)
def test_public_client_never_contacts_local_service(
    local_http: tuple[str, queue.Queue[str]],
    host: str,
) -> None:
    # Given a real loopback server and equivalent numeric/hostname spellings.
    url, received = local_http
    target_url = url.replace("127.0.0.1", host, 1)
    client = HTTPClient(public_only=True, max_retries=0)
    try:
        # When requesting local content; then refuse it without contact.
        # An unsupported numeric spelling may safely fail DNS resolution too.
        with pytest.raises(NetworkingError):
            client.get(target_url + "/blocked", timeout=0.1)
        assert received.empty()
    finally:
        client.session.close()


def test_explicit_proxy_is_rejected_before_contact(
    local_http: tuple[str, queue.Queue[str]],
) -> None:
    # Given a real local server offered as a proxy to the protected client.
    url, received = local_http
    client = HTTPClient(public_only=True, max_retries=0)
    try:
        # When sending through that proxy; then reject it without contact.
        with pytest.raises(NetworkingError):
            client.get("http://8.8.8.8/", proxies={"http": url}, timeout=0.1)
        assert received.empty()
    finally:
        client.session.close()


def test_requests_redirect_reenters_the_protected_adapter(
    local_http: tuple[str, queue.Queue[str]],
) -> None:
    # Given a trusted local starting route and guarded adapters for all other URLs.
    # A real first hop is needed to exercise requests' redirect dispatch offline.
    from codomyrmex.networking._http_security import PublicHTTPAdapter

    url, received = local_http
    with requests.Session() as session:
        session.trust_env = False
        session.mount("http://", PublicHTTPAdapter(max_retries=0))
        session.mount("https://", PublicHTTPAdapter(max_retries=0))
        session.mount(url + "/redirect", HTTPAdapter(max_retries=0))
        # When the server redirects to localhost; then reject the second hop.
        with pytest.raises(
            requests.exceptions.RequestException, match="public IP address"
        ):
            session.get(url + "/redirect", timeout=0.1)
        assert received.get_nowait() == "/redirect"
        assert received.empty()


def test_public_client_ignores_environment_proxies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given proxy environment variables and an actual protected Session.
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
        monkeypatch.setenv(name, "http://127.0.0.1:1")
    client = HTTPClient(public_only=True)
    try:
        # When merging requests options; then environment proxies stay absent.
        settings = client.session.merge_environment_settings(
            "https://8.8.8.8/", {}, False, True, None
        )
        assert settings["proxies"] == {}
    finally:
        client.session.close()


def test_public_client_refuses_disabled_tls_verification() -> None:
    # Given a protected client; when TLS authentication is disabled; then refuse.
    client = HTTPClient(public_only=True, max_retries=0)
    try:
        with pytest.raises(NetworkingError):
            client.get("https://8.8.8.8/", verify=False, timeout=0.1)
    finally:
        client.session.close()
