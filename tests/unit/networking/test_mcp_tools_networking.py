"""Tests for networking MCP tools.

Zero-mock tests that exercise the real networking MCP tool implementations.
"""

from __future__ import annotations

import pytest


class TestNetworkingListInterfaces:
    """Tests for networking_list_interfaces MCP tool."""

    def test_returns_success_status(self):
        from codomyrmex.networking.mcp_tools import networking_list_interfaces

        result = networking_list_interfaces()
        assert result["status"] == "success"

    def test_contains_hostname(self):
        from codomyrmex.networking.mcp_tools import networking_list_interfaces

        result = networking_list_interfaces()
        assert "hostname" in result
        assert isinstance(result["hostname"], str)
        assert len(result["hostname"]) > 0

    def test_contains_addresses_list(self):
        from codomyrmex.networking.mcp_tools import networking_list_interfaces

        result = networking_list_interfaces()
        assert "addresses" in result
        assert isinstance(result["addresses"], list)

    def test_address_entries_have_ip_and_family(self):
        from codomyrmex.networking.mcp_tools import networking_list_interfaces

        result = networking_list_interfaces()
        if result["addresses"]:
            entry = result["addresses"][0]
            assert "ip" in entry
            assert "family" in entry


class TestNetworkingCheckConnectivity:
    """Tests for networking_check_connectivity MCP tool."""

    @pytest.mark.network
    def test_returns_success_status(self):
        from codomyrmex.networking.mcp_tools import networking_check_connectivity

        result = networking_check_connectivity(timeout=2)
        assert result["status"] == "success"

    @pytest.mark.network
    def test_results_contain_host_and_port(self):
        from codomyrmex.networking.mcp_tools import networking_check_connectivity

        result = networking_check_connectivity(timeout=2)
        assert "results" in result
        assert len(result["results"]) == 2
        for entry in result["results"]:
            assert "host" in entry
            assert "port" in entry
            assert "reachable" in entry


class TestNetworkingListExceptions:
    """Tests for networking_list_exceptions MCP tool."""

    def test_returns_success_status(self):
        from codomyrmex.networking.mcp_tools import networking_list_exceptions

        result = networking_list_exceptions()
        assert result["status"] == "success"

    def test_contains_exception_list(self):
        from codomyrmex.networking.mcp_tools import networking_list_exceptions

        result = networking_list_exceptions()
        assert "exceptions" in result
        assert isinstance(result["exceptions"], list)
        assert len(result["exceptions"]) >= 5

    def test_exception_entries_have_name_and_base(self):
        from codomyrmex.networking.mcp_tools import networking_list_exceptions

        result = networking_list_exceptions()
        for entry in result["exceptions"]:
            assert "name" in entry
            assert "base" in entry

    def test_known_exceptions_present(self):
        from codomyrmex.networking.mcp_tools import networking_list_exceptions

        result = networking_list_exceptions()
        names = {e["name"] for e in result["exceptions"]}
        assert "HTTPError" in names
        assert "SSLError" in names
        assert "WebSocketError" in names
