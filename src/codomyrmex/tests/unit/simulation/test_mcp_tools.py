"""Strictly zero-mock tests for the simulation module's MCP tools.

Follows the zero-mock policy. Avoids patching internal dependencies.
"""

import pytest

from codomyrmex.simulation.mcp_tools import (
    _simulators,
    simulation_get_results,
    simulation_run,
)


@pytest.fixture(autouse=True)
def reset_simulators():
    """Reset the module-level simulators dictionary before and after each test."""
    _simulators.clear()
    yield
    _simulators.clear()


def test_simulation_run_success():
    """Test successful execution of a simulation via the run tool."""
    result = simulation_run(name="test_sim", max_steps=10)

    assert "error" not in result
    assert result["status"] == "success"
    assert result["steps_completed"] == 10
    assert result["config"] == "test_sim"
    assert result["simulation_status"] == "completed"

    # Verify the simulator was stored in the registry
    assert "test_sim" in _simulators


def test_simulation_run_invalid_max_steps():
    """Test that simulation_run handles invalid max_steps properly."""
    result = simulation_run(name="test_sim", max_steps=-1)

    assert "error" in result
    assert result["error"] == "max_steps must be a positive integer"

    result = simulation_run(name="test_sim", max_steps="100")  # type: ignore[arg-type]

    assert "error" in result
    assert result["error"] == "max_steps must be a positive integer"


def test_simulation_run_invalid_name():
    """Test that simulation_run handles invalid name properly."""
    result = simulation_run(name="")

    assert "error" in result
    assert result["error"] == "name must be a non-empty string"


def test_simulation_get_results_success():
    """Test successful retrieval of simulation results."""
    # First run a simulation
    simulation_run(name="get_results_sim", max_steps=5)

    # Then get its results
    result = simulation_get_results(name="get_results_sim")

    assert "error" not in result
    assert result["status"] == "success"
    assert result["steps_completed"] == 5
    assert result["config"] == "get_results_sim"
    assert result["simulation_status"] == "completed"


def test_simulation_get_results_invalid_name():
    """Test that simulation_get_results handles invalid name properly."""
    result = simulation_get_results(name="")

    assert "error" in result
    assert result["error"] == "name must be a non-empty string"


def test_simulation_get_results_not_found():
    """Test that simulation_get_results handles non-existent simulation name."""
    result = simulation_get_results(name="non_existent_sim")

    assert "error" in result
    assert "Simulation not found" in result["error"]
