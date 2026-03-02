"""
Unit tests for networking.exceptions — Zero-Mock compliant.

Covers: ConnectionError, NetworkTimeoutError, SSLError, HTTPError,
DNSResolutionError, WebSocketError, ProxyError, RateLimitError,
SSHError — context field storage, inheritance, raise/catch patterns.
"""

import pytest

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.networking.exceptions import (
    ConnectionError,
    DNSResolutionError,
    HTTPError,
    NetworkTimeoutError,
    ProxyError,
    RateLimitError,
    SSHError,
    SSLError,
    WebSocketError,
)

# ── ConnectionError ────────────────────────────────────────────────────


@pytest.mark.unit
class TestConnectionError:
    def test_is_codomyrmex_error(self):
        e = ConnectionError("conn fail")
        assert isinstance(e, CodomyrmexError)

    def test_message_set(self):
        e = ConnectionError("host unreachable")
        assert "host unreachable" in str(e)

    def test_host_stored(self):
        e = ConnectionError("fail", host="example.com")
        assert e.context["host"] == "example.com"

    def test_port_stored(self):
        e = ConnectionError("fail", port=8080)
        assert e.context["port"] == 8080

    def test_port_zero_stored(self):
        e = ConnectionError("fail", port=0)
        assert "port" in e.context
        assert e.context["port"] == 0

    def test_protocol_stored(self):
        e = ConnectionError("fail", protocol="TCP")
        assert e.context["protocol"] == "TCP"

    def test_none_fields_not_stored(self):
        e = ConnectionError("fail")
        assert "host" not in e.context
        assert "port" not in e.context
        assert "protocol" not in e.context

    def test_all_fields_stored(self):
        e = ConnectionError("fail", host="h", port=443, protocol="TLS")
        assert e.context["host"] == "h"
        assert e.context["port"] == 443
        assert e.context["protocol"] == "TLS"

    def test_raise_and_catch(self):
        with pytest.raises(ConnectionError, match="refused"):
            raise ConnectionError("connection refused", host="db.local")


# ── NetworkTimeoutError ────────────────────────────────────────────────


@pytest.mark.unit
class TestNetworkTimeoutError:
    def test_is_codomyrmex_error(self):
        e = NetworkTimeoutError("timeout")
        assert isinstance(e, CodomyrmexError)

    def test_timeout_seconds_stored(self):
        e = NetworkTimeoutError("timeout", timeout_seconds=30.0)
        assert e.context["timeout_seconds"] == pytest.approx(30.0)

    def test_timeout_zero_stored(self):
        e = NetworkTimeoutError("timeout", timeout_seconds=0.0)
        assert "timeout_seconds" in e.context

    def test_operation_stored(self):
        e = NetworkTimeoutError("timeout", operation="connect")
        assert e.context["operation"] == "connect"

    def test_url_stored(self):
        e = NetworkTimeoutError("timeout", url="https://api.example.com/v1")
        assert e.context["url"] == "https://api.example.com/v1"

    def test_none_fields_not_stored(self):
        e = NetworkTimeoutError("timeout")
        assert "timeout_seconds" not in e.context
        assert "operation" not in e.context
        assert "url" not in e.context

    def test_all_fields(self):
        e = NetworkTimeoutError("t", timeout_seconds=5.0, operation="read", url="http://x")
        assert e.context["timeout_seconds"] == pytest.approx(5.0)
        assert e.context["operation"] == "read"
        assert e.context["url"] == "http://x"


# ── SSLError ───────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSSLError:
    def test_is_codomyrmex_error(self):
        e = SSLError("ssl fail")
        assert isinstance(e, CodomyrmexError)

    def test_host_stored(self):
        e = SSLError("fail", host="secure.example.com")
        assert e.context["host"] == "secure.example.com"

    def test_certificate_error_stored(self):
        e = SSLError("fail", certificate_error="CERTIFICATE_VERIFY_FAILED")
        assert e.context["certificate_error"] == "CERTIFICATE_VERIFY_FAILED"

    def test_ssl_version_stored(self):
        e = SSLError("fail", ssl_version="TLSv1.3")
        assert e.context["ssl_version"] == "TLSv1.3"

    def test_none_fields_not_stored(self):
        e = SSLError("fail")
        assert "host" not in e.context
        assert "certificate_error" not in e.context
        assert "ssl_version" not in e.context

    def test_all_fields(self):
        e = SSLError("fail", host="h", certificate_error="expired", ssl_version="TLS1.2")
        assert e.context["host"] == "h"
        assert e.context["certificate_error"] == "expired"
        assert e.context["ssl_version"] == "TLS1.2"


# ── HTTPError ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestHTTPError:
    def test_is_codomyrmex_error(self):
        e = HTTPError("http fail")
        assert isinstance(e, CodomyrmexError)

    def test_status_code_stored(self):
        e = HTTPError("fail", status_code=404)
        assert e.context["status_code"] == 404

    def test_status_code_zero_stored(self):
        e = HTTPError("fail", status_code=0)
        assert "status_code" in e.context

    def test_url_stored(self):
        e = HTTPError("fail", url="https://api.example.com/users")
        assert e.context["url"] == "https://api.example.com/users"

    def test_method_stored(self):
        e = HTTPError("fail", method="POST")
        assert e.context["method"] == "POST"

    def test_response_body_short_stored_as_is(self):
        short_body = "Not Found"
        e = HTTPError("fail", response_body=short_body)
        assert e.context["response_body"] == short_body

    def test_response_body_long_truncated_at_500(self):
        long_body = "x" * 600
        e = HTTPError("fail", response_body=long_body)
        # Should be truncated to 500 + "..."
        assert len(e.context["response_body"]) == 503
        assert e.context["response_body"].endswith("...")

    def test_response_body_exactly_500_not_truncated(self):
        body = "y" * 500
        e = HTTPError("fail", response_body=body)
        assert e.context["response_body"] == body
        assert not e.context["response_body"].endswith("...")

    def test_none_fields_not_stored(self):
        e = HTTPError("fail")
        assert "status_code" not in e.context
        assert "url" not in e.context
        assert "method" not in e.context
        assert "response_body" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(HTTPError):
            raise HTTPError("server error", status_code=500, method="GET")


# ── DNSResolutionError ─────────────────────────────────────────────────


@pytest.mark.unit
class TestDNSResolutionError:
    def test_is_codomyrmex_error(self):
        e = DNSResolutionError("dns fail")
        assert isinstance(e, CodomyrmexError)

    def test_hostname_stored(self):
        e = DNSResolutionError("fail", hostname="nonexistent.example.com")
        assert e.context["hostname"] == "nonexistent.example.com"

    def test_dns_server_stored(self):
        e = DNSResolutionError("fail", dns_server="8.8.8.8")
        assert e.context["dns_server"] == "8.8.8.8"

    def test_none_fields_not_stored(self):
        e = DNSResolutionError("fail")
        assert "hostname" not in e.context
        assert "dns_server" not in e.context

    def test_both_fields(self):
        e = DNSResolutionError("fail", hostname="h", dns_server="1.1.1.1")
        assert e.context["hostname"] == "h"
        assert e.context["dns_server"] == "1.1.1.1"


# ── WebSocketError ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestWebSocketError:
    def test_is_codomyrmex_error(self):
        e = WebSocketError("ws fail")
        assert isinstance(e, CodomyrmexError)

    def test_url_stored(self):
        e = WebSocketError("fail", url="wss://ws.example.com/socket")
        assert e.context["url"] == "wss://ws.example.com/socket"

    def test_close_code_stored(self):
        e = WebSocketError("fail", close_code=1001)
        assert e.context["close_code"] == 1001

    def test_close_code_zero_stored(self):
        e = WebSocketError("fail", close_code=0)
        assert "close_code" in e.context
        assert e.context["close_code"] == 0

    def test_close_reason_stored(self):
        e = WebSocketError("fail", close_reason="going away")
        assert e.context["close_reason"] == "going away"

    def test_none_fields_not_stored(self):
        e = WebSocketError("fail")
        assert "url" not in e.context
        assert "close_code" not in e.context
        assert "close_reason" not in e.context

    def test_all_fields(self):
        e = WebSocketError("fail", url="wss://x", close_code=1000, close_reason="normal")
        assert e.context["url"] == "wss://x"
        assert e.context["close_code"] == 1000
        assert e.context["close_reason"] == "normal"


# ── ProxyError ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestProxyError:
    def test_is_codomyrmex_error(self):
        e = ProxyError("proxy fail")
        assert isinstance(e, CodomyrmexError)

    def test_proxy_url_stored(self):
        e = ProxyError("fail", proxy_url="http://proxy.corp:3128")
        assert e.context["proxy_url"] == "http://proxy.corp:3128"

    def test_proxy_type_stored(self):
        e = ProxyError("fail", proxy_type="SOCKS5")
        assert e.context["proxy_type"] == "SOCKS5"

    def test_target_url_stored(self):
        e = ProxyError("fail", target_url="https://api.external.com")
        assert e.context["target_url"] == "https://api.external.com"

    def test_none_fields_not_stored(self):
        e = ProxyError("fail")
        assert "proxy_url" not in e.context
        assert "proxy_type" not in e.context
        assert "target_url" not in e.context

    def test_all_fields(self):
        e = ProxyError("fail", proxy_url="h", proxy_type="HTTP", target_url="t")
        assert e.context["proxy_url"] == "h"
        assert e.context["proxy_type"] == "HTTP"
        assert e.context["target_url"] == "t"


# ── RateLimitError ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestRateLimitError:
    def test_is_codomyrmex_error(self):
        e = RateLimitError("rate limited")
        assert isinstance(e, CodomyrmexError)

    def test_url_stored(self):
        e = RateLimitError("limited", url="https://api.example.com/v2")
        assert e.context["url"] == "https://api.example.com/v2"

    def test_retry_after_stored(self):
        e = RateLimitError("limited", retry_after=60.0)
        assert e.context["retry_after"] == pytest.approx(60.0)

    def test_retry_after_zero_stored(self):
        e = RateLimitError("limited", retry_after=0.0)
        assert "retry_after" in e.context

    def test_limit_type_stored(self):
        e = RateLimitError("limited", limit_type="requests_per_minute")
        assert e.context["limit_type"] == "requests_per_minute"

    def test_none_fields_not_stored(self):
        e = RateLimitError("limited")
        assert "url" not in e.context
        assert "retry_after" not in e.context
        assert "limit_type" not in e.context

    def test_all_fields(self):
        e = RateLimitError("limited", url="u", retry_after=30.0, limit_type="quota")
        assert e.context["url"] == "u"
        assert e.context["retry_after"] == pytest.approx(30.0)
        assert e.context["limit_type"] == "quota"


# ── SSHError ───────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSSHError:
    def test_is_codomyrmex_error(self):
        e = SSHError("ssh fail")
        assert isinstance(e, CodomyrmexError)

    def test_host_stored(self):
        e = SSHError("fail", host="bastion.example.com")
        assert e.context["host"] == "bastion.example.com"

    def test_port_stored(self):
        e = SSHError("fail", port=22)
        assert e.context["port"] == 22

    def test_port_zero_stored(self):
        e = SSHError("fail", port=0)
        assert "port" in e.context
        assert e.context["port"] == 0

    def test_username_stored(self):
        e = SSHError("fail", username="admin")
        assert e.context["username"] == "admin"

    def test_none_fields_not_stored(self):
        e = SSHError("fail")
        assert "host" not in e.context
        assert "port" not in e.context
        assert "username" not in e.context

    def test_all_fields(self):
        e = SSHError("fail", host="h", port=22, username="root")
        assert e.context["host"] == "h"
        assert e.context["port"] == 22
        assert e.context["username"] == "root"

    def test_raise_and_catch(self):
        with pytest.raises(SSHError, match="auth failed"):
            raise SSHError("auth failed", host="server.example.com", username="ops")
