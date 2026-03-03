"""Tests for networking MCP tools."""

import json

import pytest

from codomyrmex.networking.mcp_tools import (
    networking_http_request,
    networking_port_scan,
)


@pytest.mark.unit
def test_networking_http_request_success():
    """Test successful HTTP request via MCP tool."""
    # Using httpbin.org which is used in other networking tests for zero-mock testing
    response_json = networking_http_request(method="GET", url="http://httpbin.org/get")
    assert "status_code" in response_json

    data = json.loads(response_json)
    assert data["status_code"] == 200
    assert "url" in data["text"]


@pytest.mark.unit
def test_networking_http_request_invalid_url():
    """Test HTTP request with invalid URL."""
    response = networking_http_request(
        method="GET", url="http://thisurldoesnotexist.test"
    )
    assert "Request failed" in response


@pytest.mark.unit
def test_networking_http_request_invalid_headers():
    """Test HTTP request with invalid JSON headers."""
    response = networking_http_request(
        method="GET", url="http://httpbin.org/get", headers="invalid-json"
    )
    assert "Error parsing headers" in response


@pytest.mark.unit
def test_networking_port_scan_success():
    """Test port scanning via MCP tool."""
    # Scan a known range on localhost, some ports might be open but regardless it shouldn't crash
    response_json = networking_port_scan(
        host="127.0.0.1", start_port=8000, end_port=8005, timeout=0.1
    )

    # Check it parses as JSON
    data = json.loads(response_json)
    assert "open_ports" in data
    assert isinstance(data["open_ports"], list)


@pytest.mark.unit
def test_networking_port_scan_invalid_host():
    """Test port scanning with invalid host."""
    # This might take a bit depending on DNS resolution, so we use a very short timeout
    response = networking_port_scan(
        host="invalid.host.local", start_port=80, end_port=80, timeout=0.1
    )

    # An exception inside scan_range bubbles up or returns an empty list depending on internal error handling
    # The actual implementation of scan_range catches some errors but `socket.getaddrinfo`
    # might raise gaierror which isn't caught by the inner try-except
    assert "Scan failed" in response or "open_ports" in response
