"""Unit tests for agents.hermes.monitoring — system resource metrics.

Tests verify that _get_system_metrics returns correct structure and types
without requiring specific hardware state.
"""

from __future__ import annotations


from codomyrmex.agents.hermes.monitoring import _get_system_metrics


class TestGetSystemMetrics:
    """Verify _get_system_metrics returns valid hardware data."""

    def test_returns_dict(self) -> None:
        """Should return a dictionary."""
        result = _get_system_metrics()
        assert isinstance(result, dict)

    def test_has_required_keys(self) -> None:
        """Should contain cpu_percent, ram_usage_percent, swap_usage_percent."""
        result = _get_system_metrics()
        assert "cpu_percent" in result
        assert "ram_usage_percent" in result
        assert "swap_usage_percent" in result

    def test_values_are_numeric(self) -> None:
        """All metric values should be numeric (int or float)."""
        result = _get_system_metrics()
        for key in ("cpu_percent", "ram_usage_percent", "swap_usage_percent"):
            assert isinstance(result[key], (int, float)), f"{key} should be numeric, got {type(result[key])}"

    def test_percentages_in_valid_range(self) -> None:
        """All percentage values should be between 0 and 100."""
        result = _get_system_metrics()
        for key in ("cpu_percent", "ram_usage_percent", "swap_usage_percent"):
            assert 0.0 <= result[key] <= 100.0, f"{key}={result[key]} outside [0, 100]"

    def test_consistent_calls(self) -> None:
        """Multiple calls should return the same structure (keys unchanged)."""
        r1 = _get_system_metrics()
        r2 = _get_system_metrics()
        assert set(r1.keys()) == set(r2.keys())

    def test_ram_usage_is_stable(self) -> None:
        """RAM usage should not swing wildly between rapid calls."""
        r1 = _get_system_metrics()
        r2 = _get_system_metrics()
        # Allow up to 20% swing for rapid successive calls
        assert abs(r1["ram_usage_percent"] - r2["ram_usage_percent"]) < 20.0
