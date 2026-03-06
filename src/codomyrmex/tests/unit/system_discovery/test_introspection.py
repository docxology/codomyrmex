import os
import platform
import sys
from pathlib import Path

import pytest
from codomyrmex.system_discovery.core.context import get_system_context
from codomyrmex.system_discovery.reporting.profilers import EnvironmentProfiler, HardwareProfiler
from codomyrmex.system_discovery.reporting.status_reporter import StatusReporter


def test_hardware_profiler_real():
    """Test HardwareProfiler with real system calls (zero-mock)."""
    info = HardwareProfiler.get_hardware_info()

    assert "os" in info
    assert info["os"] == platform.system()
    assert "cpu_count" in info
    assert info["cpu_count"] > 0
    assert "gpu" in info
    assert "available" in info["gpu"]


def test_environment_profiler_real():
    """Test EnvironmentProfiler with real system calls (zero-mock)."""
    info = EnvironmentProfiler.get_environment_info()

    assert "type" in info
    assert "python" in info
    assert "version" in info["python"]
    assert info["python"]["version"] == sys.version
    assert "is_venv" in info


def test_status_reporter_real():
    """Test StatusReporter comprehensive report (zero-mock)."""
    reporter = StatusReporter()
    report = reporter.generate_comprehensive_report()

    assert "timestamp" in report
    assert "python_environment" in report
    assert "hardware" in report
    assert "dependencies" in report

    # Check some specific values
    assert report["hardware"]["os"] == platform.system()
    assert "version_string" in report["python_environment"]


def test_get_system_context_real():
    """Test get_system_context (zero-mock)."""
    # Use current directory as root for testing
    context = get_system_context(root_dir=".")

    assert "system_root" in context
    assert "os" in context
    assert "environment" in context
    assert "modules" in context
    assert "stats" in context

    # Verify context has real data
    assert context["platform"] == platform.system()
    assert context["os"]["cpu_count"] > 0


def test_gpu_detection_logic():
    """Test GPU detection logic (even if no GPU is present)."""
    gpu_info = HardwareProfiler.get_gpu_info()
    assert "available" in gpu_info
    assert isinstance(gpu_info["details"], list)


def test_python_version_checking():
    """Test Python version extraction logic."""
    py_info = EnvironmentProfiler.get_python_info()
    assert py_info["version_info"][0] == sys.version_info[0]
    assert py_info["version_info"][1] == sys.version_info[1]


def test_dependency_validation():
    """Test dependency validation in StatusReporter."""
    reporter = StatusReporter()
    deps = reporter.check_dependencies()

    assert "dependencies" in deps
    assert "available_count" in deps
    assert "total_count" in deps
    assert deps["total_count"] > 0

    # Ensure some core dependencies are checked
    assert "python-dotenv" in deps["dependencies"]
    assert "pytest" in deps["dependencies"]
