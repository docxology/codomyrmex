"""Unit tests for Hermes URL safety (tools/url_safety.py).

Zero-Mock Policy: tests use real ``ipaddress`` objects and real DNS
resolution (via ``socket.getaddrinfo``). No MagicMock patches.
"""

from __future__ import annotations

import ipaddress
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------


def _hermes_agent_root() -> Path | None:
    candidate = Path.home() / ".hermes" / "hermes-agent"
    return candidate if candidate.exists() else None


def _import_url_safety():
    """Import tools.url_safety from ~/.hermes/hermes-agent via direct path, or skip."""
    import importlib.util

    root = _hermes_agent_root()
    if root is None:
        pytest.skip("~/.hermes/hermes-agent not found — Hermes not installed")

    fpath = root / "tools" / "url_safety.py"
    if not fpath.exists():
        pytest.skip(f"{fpath} not found")

    spec = importlib.util.spec_from_file_location("hermes_url_safety", fpath)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        pytest.skip(f"hermes url_safety not loadable: {e}")
    return mod


# ---------------------------------------------------------------------------
# _is_blocked_ip()
# ---------------------------------------------------------------------------


class TestIsBlockedIp:
    """IP address blocking for SSRF prevention."""

    def test_loopback_v4_blocked(self) -> None:
        us = _import_url_safety()
        assert us._is_blocked_ip(ipaddress.ip_address("127.0.0.1")) is True

    def test_loopback_v6_blocked(self) -> None:
        us = _import_url_safety()
        assert us._is_blocked_ip(ipaddress.ip_address("::1")) is True

    def test_private_10x_blocked(self) -> None:
        us = _import_url_safety()
        assert us._is_blocked_ip(ipaddress.ip_address("10.0.0.1")) is True

    def test_private_172_16_blocked(self) -> None:
        us = _import_url_safety()
        assert us._is_blocked_ip(ipaddress.ip_address("172.16.0.1")) is True

    def test_private_192_168_blocked(self) -> None:
        us = _import_url_safety()
        assert us._is_blocked_ip(ipaddress.ip_address("192.168.1.1")) is True

    def test_link_local_blocked(self) -> None:
        us = _import_url_safety()
        # Cloud metadata endpoint range
        assert us._is_blocked_ip(ipaddress.ip_address("169.254.169.254")) is True

    def test_cgnat_blocked(self) -> None:
        us = _import_url_safety()
        assert us._is_blocked_ip(ipaddress.ip_address("100.64.0.1")) is True

    def test_cgnat_upper_bound_blocked(self) -> None:
        us = _import_url_safety()
        assert us._is_blocked_ip(ipaddress.ip_address("100.127.255.254")) is True

    def test_multicast_blocked(self) -> None:
        us = _import_url_safety()
        assert us._is_blocked_ip(ipaddress.ip_address("224.0.0.1")) is True

    def test_unspecified_blocked(self) -> None:
        us = _import_url_safety()
        assert us._is_blocked_ip(ipaddress.ip_address("0.0.0.0")) is True

    def test_public_ip_allowed(self) -> None:
        us = _import_url_safety()
        assert us._is_blocked_ip(ipaddress.ip_address("8.8.8.8")) is False

    def test_public_ip_cloudflare_allowed(self) -> None:
        us = _import_url_safety()
        assert us._is_blocked_ip(ipaddress.ip_address("1.1.1.1")) is False

    def test_public_v6_allowed(self) -> None:
        us = _import_url_safety()
        assert us._is_blocked_ip(ipaddress.ip_address("2001:4860:4860::8888")) is False


# ---------------------------------------------------------------------------
# is_safe_url()
# ---------------------------------------------------------------------------


class TestIsSafeUrl:
    """Full URL safety checks with DNS resolution."""

    def test_empty_url_blocked(self) -> None:
        us = _import_url_safety()
        assert us.is_safe_url("") is False

    def test_no_hostname_blocked(self) -> None:
        us = _import_url_safety()
        assert us.is_safe_url("http://") is False

    def test_blocked_hostname_metadata_google(self) -> None:
        us = _import_url_safety()
        assert us.is_safe_url("http://metadata.google.internal/computeMetadata/v1/") is False

    def test_blocked_hostname_metadata_goog(self) -> None:
        us = _import_url_safety()
        assert us.is_safe_url("http://metadata.goog/") is False

    def test_localhost_blocked(self) -> None:
        us = _import_url_safety()
        assert us.is_safe_url("http://localhost:8080/api") is False

    def test_loopback_ip_blocked(self) -> None:
        us = _import_url_safety()
        assert us.is_safe_url("http://127.0.0.1:9090/") is False

    def test_private_ip_blocked(self) -> None:
        us = _import_url_safety()
        assert us.is_safe_url("http://192.168.1.1/admin") is False

    def test_public_url_allowed(self) -> None:
        us = _import_url_safety()
        # google.com resolves to a public IP
        assert us.is_safe_url("https://www.google.com/") is True

    def test_dns_failure_blocked(self) -> None:
        us = _import_url_safety()
        # Intentionally unresolvable hostname → fail closed
        assert us.is_safe_url("http://this-domain-definitely-does-not-exist-xyz123.invalid/") is False

    def test_malformed_url_blocked(self) -> None:
        us = _import_url_safety()
        assert us.is_safe_url("not-a-url") is False
