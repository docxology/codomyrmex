"""Tests for networking service mesh MCP tools."""

import json

import pytest

from codomyrmex.networking.service_mesh.mcp_tools import (
    service_mesh_circuit_breaker_simulate,
    service_mesh_load_balancer_simulate,
)


@pytest.mark.unit
def test_service_mesh_circuit_breaker_simulate():
    """Test circuit breaker simulation tool."""
    # Test closed state (failures < 3)
    response_json = service_mesh_circuit_breaker_simulate("test-cb", 2)
    data = json.loads(response_json)
    assert data["name"] == "test-cb"
    assert data["state"] == "closed"
    assert data["failure_count"] == 2

    # Test open state (failures >= 3)
    response_json = service_mesh_circuit_breaker_simulate("test-cb", 3)
    data = json.loads(response_json)
    assert data["state"] == "open"
    assert data["failure_count"] == 3


@pytest.mark.unit
def test_service_mesh_load_balancer_simulate_success():
    """Test load balancer simulation with a valid strategy and instances."""
    instances = json.dumps(
        [
            {
                "id": "inst1",
                "host": "10.0.0.1",
                "port": 80,
                "weight": 1,
                "connections": 5,
            },
            {
                "id": "inst2",
                "host": "10.0.0.2",
                "port": 80,
                "weight": 2,
                "connections": 10,
            },
        ]
    )

    response_json = service_mesh_load_balancer_simulate("ROUND_ROBIN", instances)
    data = json.loads(response_json)

    # Round robin should select the first instance as the index is initialized to 0,
    # wait the implementation says self._round_robin_index = (self._round_robin_index + 1) % len(healthy)
    # returns healthy[self._round_robin_index] which will be index 1.
    assert data["selected_id"] == "inst2"


@pytest.mark.unit
def test_service_mesh_load_balancer_simulate_invalid_strategy():
    """Test load balancer simulation with invalid strategy."""
    instances = json.dumps([{"id": "inst1"}])
    response = service_mesh_load_balancer_simulate("INVALID_STRATEGY", instances)
    assert "Unknown strategy" in response


@pytest.mark.unit
def test_service_mesh_load_balancer_simulate_invalid_json():
    """Test load balancer simulation with invalid JSON for instances."""
    response = service_mesh_load_balancer_simulate("RANDOM", "{invalid_json}")
    assert "Error parsing instances" in response


@pytest.mark.unit
def test_service_mesh_load_balancer_simulate_empty():
    """Test load balancer simulation with no healthy instances."""
    response = service_mesh_load_balancer_simulate("ROUND_ROBIN", "[]")
    assert response == "No instances available"
