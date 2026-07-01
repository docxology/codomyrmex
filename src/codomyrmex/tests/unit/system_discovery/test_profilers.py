"""Tests for hardware and environment profilers."""

import pytest

from codomyrmex.system_discovery.reporting.profilers import HardwareProfiler


@pytest.mark.unit
class TestHardwareProfiler:
    """Tests for HardwareProfiler."""

    def test_get_hardware_info(self):
        """Test getting hardware info returns expected keys and types."""
        info = HardwareProfiler.get_hardware_info()

        # Should be a dictionary
        assert isinstance(info, dict)

        # Base keys
        assert "cpu_count" in info
        assert "cpu_threads" in info
        assert "os" in info
        assert "os_release" in info
        assert "os_version" in info
        assert "architecture" in info
        assert "processor" in info
        assert "gpu" in info

        # Optional keys based on psutil availability
        assert "cpu_freq" in info
        assert "total_ram_gb" in info
        assert "available_ram_gb" in info

        # Type checks
        assert isinstance(info["cpu_count"], (int, type(None)))
        assert isinstance(info["cpu_threads"], (int, type(None)))
        assert isinstance(info["os"], str)
        assert isinstance(info["os_release"], str)
        assert isinstance(info["os_version"], str)
        assert isinstance(info["architecture"], str)
        assert isinstance(info["processor"], str)
        assert isinstance(info["gpu"], dict)
        assert "available" in info["gpu"]
        assert "details" in info["gpu"]

        assert isinstance(info["cpu_freq"], (dict, type(None)))
        assert isinstance(info["total_ram_gb"], (float, int, type(None)))
        assert isinstance(info["available_ram_gb"], (float, int, type(None)))
