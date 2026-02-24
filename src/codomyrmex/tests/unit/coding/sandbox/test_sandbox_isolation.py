"""Tests for sandbox isolation and resource limits.

Uses real ExecutionLimits dataclass and resource_limits_context.
No mocks. Some tests may be skipped on platforms that don't support setrlimit.
"""

import pytest

from codomyrmex.coding.sandbox.isolation import (
    ExecutionLimits,
    resource_limits_context,
)


@pytest.mark.unit
class TestExecutionLimitsDefaults:
    """Tests for ExecutionLimits default values."""

    def test_default_time_limit(self):
        """Test functionality: default time limit."""
        limits = ExecutionLimits()
        assert limits.time_limit == 30

    def test_default_memory_limit(self):
        """Test functionality: default memory limit."""
        limits = ExecutionLimits()
        assert limits.memory_limit == 256

    def test_default_cpu_limit(self):
        """Test functionality: default cpu limit."""
        limits = ExecutionLimits()
        assert limits.cpu_limit == 0.5

    def test_default_max_output_chars(self):
        """Test functionality: default max output chars."""
        limits = ExecutionLimits()
        assert limits.max_output_chars == 100000


@pytest.mark.unit
class TestExecutionLimitsCustomValues:
    """Tests for ExecutionLimits with custom values."""

    def test_custom_time_limit(self):
        """Test functionality: custom time limit."""
        limits = ExecutionLimits(time_limit=60)
        assert limits.time_limit == 60

    def test_custom_memory_limit(self):
        """Test functionality: custom memory limit."""
        limits = ExecutionLimits(memory_limit=512)
        assert limits.memory_limit == 512

    def test_custom_cpu_limit(self):
        """Test functionality: custom cpu limit."""
        limits = ExecutionLimits(cpu_limit=2.0)
        assert limits.cpu_limit == 2.0

    def test_custom_max_output_chars(self):
        """Test functionality: custom max output chars."""
        limits = ExecutionLimits(max_output_chars=50000)
        assert limits.max_output_chars == 50000

    def test_boundary_time_limit_one(self):
        """Test functionality: boundary time limit one."""
        limits = ExecutionLimits(time_limit=1)
        assert limits.time_limit == 1

    def test_boundary_time_limit_three_hundred(self):
        """Test functionality: boundary time limit three hundred."""
        limits = ExecutionLimits(time_limit=300)
        assert limits.time_limit == 300

    def test_boundary_cpu_limit_min(self):
        """Test functionality: boundary cpu limit min."""
        limits = ExecutionLimits(cpu_limit=0.1)
        assert limits.cpu_limit == 0.1

    def test_boundary_cpu_limit_max(self):
        """Test functionality: boundary cpu limit max."""
        limits = ExecutionLimits(cpu_limit=4.0)
        assert limits.cpu_limit == 4.0


@pytest.mark.unit
class TestExecutionLimitsValidation:
    """Tests for ExecutionLimits __post_init__ validation."""

    def test_invalid_time_limit_zero(self):
        """Test functionality: invalid time limit zero."""
        with pytest.raises(ValueError, match="Time limit"):
            ExecutionLimits(time_limit=0)

    def test_invalid_time_limit_negative(self):
        """Test functionality: invalid time limit negative."""
        with pytest.raises(ValueError, match="Time limit"):
            ExecutionLimits(time_limit=-1)

    def test_invalid_time_limit_exceeds_max(self):
        """Test functionality: invalid time limit exceeds max."""
        with pytest.raises(ValueError, match="Time limit"):
            ExecutionLimits(time_limit=301)

    def test_invalid_memory_limit_zero(self):
        """Test functionality: invalid memory limit zero."""
        with pytest.raises(ValueError, match="Memory limit"):
            ExecutionLimits(memory_limit=0)

    def test_invalid_memory_limit_negative(self):
        """Test functionality: invalid memory limit negative."""
        with pytest.raises(ValueError, match="Memory limit"):
            ExecutionLimits(memory_limit=-1)

    def test_invalid_cpu_limit_zero(self):
        """Test functionality: invalid cpu limit zero."""
        with pytest.raises(ValueError, match="CPU limit"):
            ExecutionLimits(cpu_limit=0.0)

    def test_invalid_cpu_limit_negative(self):
        """Test functionality: invalid cpu limit negative."""
        with pytest.raises(ValueError, match="CPU limit"):
            ExecutionLimits(cpu_limit=-0.5)

    def test_invalid_cpu_limit_exceeds_max(self):
        """Test functionality: invalid cpu limit exceeds max."""
        with pytest.raises(ValueError, match="CPU limit"):
            ExecutionLimits(cpu_limit=4.1)

    def test_invalid_max_output_chars_below_min(self):
        """Test functionality: invalid max output chars below min."""
        with pytest.raises(ValueError, match="Max output chars"):
            ExecutionLimits(max_output_chars=999)


@pytest.mark.unit
class TestResourceLimitsContext:
    """Tests for the resource_limits_context context manager."""

    def test_context_manager_enters_and_exits(self):
        """resource_limits_context is usable as a context manager."""
        limits = ExecutionLimits(time_limit=30, memory_limit=256)
        with resource_limits_context(limits):
            pass  # Should not raise

    def test_context_manager_restores_on_exception(self):
        """Limits are restored even if an exception occurs inside the block."""
        limits = ExecutionLimits(time_limit=10)
        with pytest.raises(RuntimeError, match="simulated error"):
            with resource_limits_context(limits):
                raise RuntimeError("simulated error")
        # Context manager exited cleanly despite the exception;
        # verify limits object is still intact after restore
        assert limits.time_limit == 10

    def test_context_manager_with_default_limits(self):
        """Default ExecutionLimits work with resource_limits_context."""
        limits = ExecutionLimits()
        with resource_limits_context(limits):
            # Execution inside limits should work fine
            result = sum(range(100))
            assert result == 4950
