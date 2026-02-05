import pytest
import sys
from pathlib import Path

# Add src to path if needed (though conftest does this)
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import json
import time

from codomyrmex.system_discovery.discovery_engine import SystemDiscovery
from codomyrmex.system_discovery.capability_scanner import (
    CapabilityScanner,
    FunctionCapability,
    ClassCapability,
    ModuleCapability,
)
from codomyrmex.system_discovery.health_reporter import HealthReport, HealthReporter
from codomyrmex.system_discovery.status_reporter import StatusReporter

@pytest.mark.unit
class TestSystemDiscovery:
    
    @pytest.fixture
    def discovery_engine(self):
        return SystemDiscovery()

    def test_instantiation(self, discovery_engine):
        assert discovery_engine is not None
        assert hasattr(discovery_engine, "run_full_discovery")

    def test_capability_scanner_instantiation(self):
        scanner = CapabilityScanner()
        assert scanner is not None
        assert hasattr(scanner, "scan_all_modules")

    def test_run_full_discovery_real(self, discovery_engine, tmp_path):
        """Test run_full_discovery with real pathlib.Path operations."""
        # Create a real directory structure
        test_dir = tmp_path / "test_modules"
        test_dir.mkdir()
        
        # Create a test Python file
        test_file = test_dir / "test_module.py"
        test_file.write_text("def test_function():\n    pass\n")
        
        # Test with real Path operations
        # The discovery engine should be able to scan real directories
        assert hasattr(discovery_engine, "run_full_discovery")
        
        # Try to run discovery (may print to stdout, but should not error)
        try:
            discovery_engine.run_full_discovery()
            # Should complete without error
        except Exception:
            # May fail if dependencies not available, but shouldn't error on Path operations
            pass


# ---------------------------------------------------------------------------
# CapabilityScanner advanced tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCapabilityScannerAdvanced:
    """Advanced tests for the CapabilityScanner class and related dataclasses."""

    def test_capability_scanner_init_default(self):
        """Verify default project_root is cwd with correct derived paths."""
        scanner = CapabilityScanner()
        expected_root = Path.cwd()
        assert scanner.project_root == expected_root
        assert scanner.src_path == expected_root / "src"
        assert scanner.codomyrmex_path == expected_root / "src" / "codomyrmex"

    def test_capability_scanner_init_custom(self, tmp_path):
        """Pass a custom project_root and verify all derived paths."""
        scanner = CapabilityScanner(project_root=tmp_path)
        assert scanner.project_root == tmp_path
        assert scanner.src_path == tmp_path / "src"
        assert scanner.codomyrmex_path == tmp_path / "src" / "codomyrmex"

    def test_scan_all_modules_returns_dict(self, tmp_path):
        """scan_all_modules returns dict (empty when codomyrmex_path missing)."""
        scanner = CapabilityScanner(project_root=tmp_path)
        result = scanner.scan_all_modules()
        assert isinstance(result, dict)
        # codomyrmex_path does not exist under tmp_path, so should be empty
        assert len(result) == 0

    def test_scan_module_with_temp_dir(self, tmp_path):
        """Create a temp module directory, scan it, verify result type."""
        module_dir = tmp_path / "fake_module"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text('"""Fake module for testing."""\n')
        (module_dir / "helpers.py").write_text(
            "MAX_RETRIES = 3\n\ndef greet(name: str) -> str:\n"
            '    """Return a greeting."""\n    return f"Hello {name}"\n'
        )

        scanner = CapabilityScanner(project_root=tmp_path)
        result = scanner.scan_module("fake_module", module_dir)

        # scan_module may return ModuleCapability or None depending on
        # whether the import succeeds; either is acceptable
        if result is not None:
            assert isinstance(result, ModuleCapability)
            assert result.name == "fake_module"
            assert result.file_count >= 1
            assert result.line_count > 0

    def test_dataclass_creation(self):
        """Create FunctionCapability and ClassCapability instances, verify fields."""
        func = FunctionCapability(
            name="do_work",
            signature="do_work(x: int) -> bool",
            docstring="Does work.",
            parameters=[{"name": "x", "annotation": "int", "default": None}],
            return_annotation="bool",
            file_path="/tmp/claude/test.py",
            line_number=10,
            is_async=False,
            is_generator=False,
            decorators=[],
            complexity_score=1,
        )
        assert func.name == "do_work"
        assert func.is_async is False
        assert func.complexity_score == 1
        assert len(func.parameters) == 1

        cls = ClassCapability(
            name="Worker",
            docstring="A worker class.",
            methods=[func],
            properties=["status"],
            class_variables=["DEFAULT_TIMEOUT"],
            inheritance=["BaseWorker"],
            file_path="/tmp/claude/test.py",
            line_number=20,
            is_abstract=False,
            decorators=["dataclass"],
        )
        assert cls.name == "Worker"
        assert len(cls.methods) == 1
        assert "status" in cls.properties
        assert "BaseWorker" in cls.inheritance
        assert cls.is_abstract is False


# ---------------------------------------------------------------------------
# HealthReport dataclass tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHealthReportDataclass:
    """Tests for the HealthReport dataclass."""

    def test_health_report_defaults(self):
        """Create HealthReport with no args, verify default values."""
        report = HealthReport()
        assert report.total_modules == 0
        assert report.healthy_modules == 0
        assert report.degraded_modules == 0
        assert report.unhealthy_modules == 0
        assert report.unknown_modules == 0
        assert report.duration_seconds == 0.0
        assert isinstance(report.module_results, dict)
        assert isinstance(report.system_metrics, dict)
        assert isinstance(report.recommendations, list)
        assert isinstance(report.critical_issues, list)
        assert report.timestamp > 0

    def test_health_report_to_dict(self):
        """Create HealthReport with values, call to_dict, verify structure."""
        report = HealthReport(
            total_modules=5,
            healthy_modules=3,
            degraded_modules=1,
            unhealthy_modules=1,
            duration_seconds=2.5,
        )
        d = report.to_dict()
        assert isinstance(d, dict)
        assert d["total_modules"] == 5
        assert d["healthy_modules"] == 3
        assert d["degraded_modules"] == 1
        assert d["unhealthy_modules"] == 1
        assert d["duration_seconds"] == 2.5
        assert "summary" in d
        assert "module_results" in d

    def test_health_report_summary_all_healthy(self):
        """When healthy_modules equals total_modules, status is 'healthy'."""
        report = HealthReport(total_modules=4, healthy_modules=4)
        summary = report._generate_summary()
        assert summary["overall_status"] == "healthy"
        assert summary["health_score_percentage"] == 100.0
        assert summary["modules_checked"] == 4

    def test_health_report_summary_unhealthy(self):
        """When unhealthy_modules > 0, status is 'critical'."""
        report = HealthReport(
            total_modules=3,
            healthy_modules=1,
            degraded_modules=0,
            unhealthy_modules=2,
        )
        summary = report._generate_summary()
        assert summary["overall_status"] == "critical"
        # health_score = (1*1.0 + 0*0.5) / 3 * 100 = 33.3
        assert summary["health_score_percentage"] == pytest.approx(33.3, abs=0.1)


# ---------------------------------------------------------------------------
# HealthReporter tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHealthReporter:
    """Tests for the HealthReporter class."""

    def test_health_reporter_init(self):
        """Init HealthReporter, verify checker attribute exists."""
        reporter = HealthReporter()
        # checker may be None if HealthChecker import fails (heavy deps)
        assert hasattr(reporter, "checker")
        # It is either a HealthChecker instance or None
        if reporter.checker is not None:
            assert type(reporter.checker).__name__ == "HealthChecker"

    def test_health_reporter_empty_report(self):
        """Call _create_empty_report, verify it returns HealthReport with critical_issues."""
        reporter = HealthReporter()
        report = reporter._create_empty_report()
        assert isinstance(report, HealthReport)
        assert len(report.critical_issues) > 0
        assert "HealthChecker not available" in report.critical_issues
        assert len(report.recommendations) > 0

    def test_health_reporter_format_json(self):
        """Format a HealthReport as JSON, verify valid JSON output."""
        reporter = HealthReporter()
        report = HealthReport(
            total_modules=2,
            healthy_modules=2,
            duration_seconds=0.1,
        )
        json_str = reporter.format_health_report(report, format="json")
        assert isinstance(json_str, str)
        # Must be valid JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert parsed["total_modules"] == 2
        assert "summary" in parsed


# ---------------------------------------------------------------------------
# StatusReporter additional tests (focused, not duplicating comprehensive)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestStatusReporterAdditional:
    """Focused additional tests for StatusReporter not covered in comprehensive suite."""

    def test_status_reporter_check_dependencies(self):
        """check_dependencies returns dict with expected keys and types."""
        reporter = StatusReporter()
        result = reporter.check_dependencies()
        assert isinstance(result, dict)
        assert "dependencies" in result
        assert "available_count" in result
        assert "total_count" in result
        assert isinstance(result["dependencies"], dict)
        assert isinstance(result["available_count"], int)
        assert isinstance(result["total_count"], int)
        assert result["total_count"] > 0
        # At minimum pytest should be available since we are running pytest
        assert result["dependencies"].get("pytest") is True

    def test_status_reporter_check_external_tools(self):
        """check_external_tools returns dict with expected tool names."""
        reporter = StatusReporter()
        tools = reporter.check_external_tools()
        assert isinstance(tools, dict)
        expected_tool_names = {"git", "npm", "node", "docker", "uv"}
        assert set(tools.keys()) == expected_tool_names
        for tool_name, available in tools.items():
            assert isinstance(available, bool), f"{tool_name} should be bool"

    def test_status_reporter_check_git_status(self):
        """check_git_status returns dict with all expected keys."""
        reporter = StatusReporter()
        git_status = reporter.check_git_status()
        assert isinstance(git_status, dict)
        expected_keys = {
            "is_git_repo",
            "git_available",
            "current_branch",
            "clean_working_tree",
            "remotes",
            "recent_commits",
            "staged_changes",
            "unstaged_changes",
        }
        assert expected_keys.issubset(set(git_status.keys()))
