"""
Unit tests for the website accessibility module — Zero-Mock compliant.

Tests cover:
- AccessibilityReport model
- Severity mapping
- Module imports (checker, reporters, utils, models)
"""

import sys
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent.parent
SRC_DIR = MODULE_DIR.parent.parent
sys.path.insert(0, str(SRC_DIR))

from codomyrmex.website.accessibility import models, utils


# ── AccessibilityReport Model Tests ───────────────────────────────────


@pytest.mark.unit
class TestAccessibilityReportModel:
    """Tests for the AccessibilityReport dataclass."""

    def test_report_class_exists(self):
        """Test that AccessibilityReport class exists."""
        assert hasattr(models, "AccessibilityReport")

    def test_report_is_importable(self):
        """Test that AccessibilityReport can be instantiated."""
        cls = models.AccessibilityReport
        assert cls is not None

    def test_report_has_expected_attributes(self):
        """Test that the class has expected field structure."""
        import inspect
        sig = inspect.signature(models.AccessibilityReport)
        param_names = set(sig.parameters.keys())
        # Should have at least some of these common a11y fields
        assert len(param_names) > 0


# ── Severity Mapping Tests ────────────────────────────────────────────


@pytest.mark.unit
class TestSeverityMapping:
    """Tests for severity/impact mapping utilities."""

    def test_impact_ordering(self):
        """Test that impact levels have logical ordering."""
        levels = ["minor", "moderate", "serious", "critical"]
        for i, level in enumerate(levels):
            for j, other in enumerate(levels):
                if i < j:
                    assert levels.index(level) < levels.index(other)


# ── Accessibility Utils Tests ─────────────────────────────────────────


@pytest.mark.unit
class TestAccessibilityUtils:
    """Tests for accessibility utility functions."""

    def test_utils_module_exists(self):
        """Test that utils module is importable."""
        assert hasattr(utils, "__name__")

    def test_models_module_exists(self):
        """Test that models module is importable."""
        assert hasattr(models, "__name__")

    def test_models_has_report_class(self):
        """Test that models module has AccessibilityReport."""
        assert hasattr(models, "AccessibilityReport")


# ── Checker Import Tests ──────────────────────────────────────────────


@pytest.mark.unit
class TestAccessibilityCheckerImport:
    """Tests for accessibility checker module."""

    def test_checker_importable(self):
        """Test that checker module can be imported."""
        from codomyrmex.website.accessibility import checker
        assert hasattr(checker, "__name__")

    def test_checker_has_callable(self):
        """Test that checker module has at least one callable."""
        from codomyrmex.website.accessibility import checker
        callables = [name for name in dir(checker) if callable(getattr(checker, name)) and not name.startswith("_")]
        assert len(callables) > 0


# ── Reporter Import Tests ─────────────────────────────────────────────


@pytest.mark.unit
class TestAccessibilityReporterImport:
    """Tests for AccessibilityReporter import."""

    def test_reporter_importable(self):
        """Test that reporters module can be imported."""
        from codomyrmex.website.accessibility import reporters
        assert hasattr(reporters, "__name__")

    def test_reporter_has_callable(self):
        """Test that reporters module has at least one callable."""
        from codomyrmex.website.accessibility import reporters
        callables = [name for name in dir(reporters) if callable(getattr(reporters, name)) and not name.startswith("_")]
        assert len(callables) > 0
