"""Unit tests for codomyrmex.system_discovery.health.health_reporter module.

Covers:
- HealthReport dataclass: construction, field defaults, to_dict, _generate_summary
- HealthReport summary logic: health_score formula, overall_status determination
- HealthReporter: __init__, generate_health_report, _create_empty_report
- HealthReporter: _generate_overall_recommendations (unhealthy, unknown, metrics)
- HealthReporter: format_health_report in text, json, and markdown formats
- HealthReporter: _format_text_report and _format_markdown_report content
- HealthReporter: export_health_report (file creation, format inference by extension)
- HealthReporter: compare_health_reports (score change, module deltas, issue deltas)
- Module-level convenience functions: generate_health_report, format_health_report,
  export_health_report
"""

import json
import time
from pathlib import Path

import pytest

# Patch missing symbol so the health_checker import chain resolves.
# codomyrmex.logging_monitoring does not export log_with_context; this
# one-time patch at module level allows all imports to succeed.
import codomyrmex.logging_monitoring as _lm

if not hasattr(_lm, "log_with_context"):
    _lm.log_with_context = lambda level, msg, ctx=None: None

from codomyrmex.system_discovery.health.health_checker import (
    HealthCheckResult,
    HealthStatus,
)
from codomyrmex.system_discovery.health.health_reporter import (
    HealthReport,
    HealthReporter,
    export_health_report,
    format_health_report,
    generate_health_report,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_result(
    name: str,
    status: HealthStatus,
    issues: list[str] | None = None,
    recommendations: list[str] | None = None,
) -> HealthCheckResult:
    """Build a real HealthCheckResult for use in report tests."""
    result = HealthCheckResult(module_name=name, status=status)
    for issue in issues or []:
        result.add_issue(issue)
    for rec in recommendations or []:
        result.recommendations.append(rec)
    return result


def _make_healthy_report(n: int = 3) -> HealthReport:
    """Create a HealthReport with n healthy modules."""
    report = HealthReport()
    report.total_modules = n
    report.healthy_modules = n
    for i in range(n):
        result = _make_result(f"mod_{i}", HealthStatus.HEALTHY)
        report.module_results[f"mod_{i}"] = result
    return report


# ===================================================================
# HealthReport dataclass — construction and defaults
# ===================================================================


@pytest.mark.unit
class TestHealthReportDefaults:
    """Test HealthReport default field values at construction time."""

    def test_timestamp_is_recent(self):
        before = time.time()
        report = HealthReport()
        after = time.time()
        assert before <= report.timestamp <= after

    def test_duration_seconds_default_zero(self):
        report = HealthReport()
        assert report.duration_seconds == 0.0

    def test_module_counts_default_zero(self):
        report = HealthReport()
        assert report.total_modules == 0
        assert report.healthy_modules == 0
        assert report.degraded_modules == 0
        assert report.unhealthy_modules == 0
        assert report.unknown_modules == 0

    def test_collections_default_empty(self):
        report = HealthReport()
        assert report.module_results == {}
        assert report.system_metrics == {}
        assert report.recommendations == []
        assert report.critical_issues == []

    def test_can_set_all_fields(self):
        report = HealthReport()
        report.total_modules = 5
        report.healthy_modules = 3
        report.degraded_modules = 1
        report.unhealthy_modules = 1
        report.duration_seconds = 1.5
        assert report.total_modules == 5
        assert report.healthy_modules == 3
        assert report.duration_seconds == 1.5


# ===================================================================
# HealthReport.to_dict
# ===================================================================


@pytest.mark.unit
class TestHealthReportToDict:
    """Test HealthReport.to_dict serialises all fields correctly."""

    def test_to_dict_has_all_keys(self):
        report = HealthReport()
        d = report.to_dict()
        expected_keys = {
            "timestamp",
            "duration_seconds",
            "total_modules",
            "healthy_modules",
            "degraded_modules",
            "unhealthy_modules",
            "unknown_modules",
            "module_results",
            "system_metrics",
            "recommendations",
            "critical_issues",
            "summary",
        }
        assert expected_keys.issubset(d.keys())

    def test_module_results_serialised_as_dict(self):
        report = HealthReport()
        result = _make_result("logging", HealthStatus.HEALTHY)
        report.module_results["logging"] = result
        d = report.to_dict()
        assert "logging" in d["module_results"]
        assert isinstance(d["module_results"]["logging"], dict)

    def test_numeric_fields_round_trip(self):
        report = HealthReport()
        report.total_modules = 7
        report.healthy_modules = 4
        report.degraded_modules = 2
        report.unhealthy_modules = 1
        report.duration_seconds = 3.14
        d = report.to_dict()
        assert d["total_modules"] == 7
        assert d["healthy_modules"] == 4
        assert d["duration_seconds"] == pytest.approx(3.14)

    def test_lists_round_trip(self):
        report = HealthReport()
        report.recommendations.append("rec1")
        report.critical_issues.append("issue1")
        d = report.to_dict()
        assert "rec1" in d["recommendations"]
        assert "issue1" in d["critical_issues"]

    def test_summary_embedded(self):
        report = HealthReport()
        report.total_modules = 2
        report.healthy_modules = 2
        d = report.to_dict()
        assert "summary" in d
        assert isinstance(d["summary"], dict)


# ===================================================================
# HealthReport._generate_summary — health score and overall_status
# ===================================================================


@pytest.mark.unit
class TestHealthReportGenerateSummary:
    """Test the health score calculation and overall_status logic."""

    def test_empty_report_score_zero(self):
        # With total_modules=0, score is 0. Status: healthy_modules(0)==total_modules(0)
        # so the source code sets overall_status="healthy" (vacuously all healthy).
        report = HealthReport()
        summary = report._generate_summary()
        assert summary["health_score_percentage"] == 0.0
        # Source code: elif healthy_modules == total_modules -> "healthy" (0 == 0)
        assert summary["overall_status"] == "healthy"

    def test_all_healthy_score_100(self):
        report = HealthReport()
        report.total_modules = 4
        report.healthy_modules = 4
        summary = report._generate_summary()
        assert summary["health_score_percentage"] == 100.0
        assert summary["overall_status"] == "healthy"

    def test_all_unhealthy_status_critical(self):
        report = HealthReport()
        report.total_modules = 2
        report.unhealthy_modules = 2
        summary = report._generate_summary()
        assert summary["overall_status"] == "critical"

    def test_degraded_status_warning(self):
        report = HealthReport()
        report.total_modules = 2
        report.healthy_modules = 1
        report.degraded_modules = 1
        summary = report._generate_summary()
        assert summary["overall_status"] == "warning"

    def test_unhealthy_takes_priority_over_degraded(self):
        report = HealthReport()
        report.total_modules = 3
        report.healthy_modules = 1
        report.degraded_modules = 1
        report.unhealthy_modules = 1
        summary = report._generate_summary()
        # unhealthy_modules > 0 makes it critical regardless of degraded
        assert summary["overall_status"] == "critical"

    def test_mixed_score_calculation(self):
        # 2 healthy (x1.0) + 2 degraded (x0.5) = 3.0 / 4 = 75%
        report = HealthReport()
        report.total_modules = 4
        report.healthy_modules = 2
        report.degraded_modules = 2
        summary = report._generate_summary()
        assert summary["health_score_percentage"] == pytest.approx(75.0)

    def test_modules_checked_matches_total(self):
        report = HealthReport()
        report.total_modules = 9
        report.healthy_modules = 9
        summary = report._generate_summary()
        assert summary["modules_checked"] == 9

    def test_issues_count_aggregates_module_issues(self):
        report = HealthReport()
        report.total_modules = 1
        report.healthy_modules = 1
        result = _make_result("mod", HealthStatus.HEALTHY, issues=["prob1", "prob2"])
        report.module_results["mod"] = result
        summary = report._generate_summary()
        # 2 module-level issues + 0 critical_issues = 2
        assert summary["issues_count"] == 2

    def test_issues_count_includes_critical_issues(self):
        report = HealthReport()
        report.critical_issues.extend(["crit1", "crit2"])
        result = _make_result("mod", HealthStatus.UNHEALTHY, issues=["mod_issue"])
        report.module_results["mod"] = result
        summary = report._generate_summary()
        assert summary["issues_count"] == 3


# ===================================================================
# HealthReporter.__init__
# ===================================================================


@pytest.mark.unit
class TestHealthReporterInit:
    """Test HealthReporter construction."""

    def test_checker_attribute_set(self):
        reporter = HealthReporter()
        # checker is either a HealthChecker instance or None (if import failed)
        assert hasattr(reporter, "checker")

    def test_checker_is_health_checker_instance(self):
        from codomyrmex.system_discovery.health.health_checker import HealthChecker

        reporter = HealthReporter()
        if reporter.checker is not None:
            assert isinstance(reporter.checker, HealthChecker)


# ===================================================================
# HealthReporter._create_empty_report
# ===================================================================


@pytest.mark.unit
class TestCreateEmptyReport:
    """Test HealthReporter._create_empty_report fallback."""

    def test_returns_health_report(self):
        reporter = HealthReporter()
        report = reporter._create_empty_report()
        assert isinstance(report, HealthReport)

    def test_has_critical_issue(self):
        reporter = HealthReporter()
        report = reporter._create_empty_report()
        assert len(report.critical_issues) >= 1
        assert any("HealthChecker" in issue for issue in report.critical_issues)

    def test_has_recommendation(self):
        reporter = HealthReporter()
        report = reporter._create_empty_report()
        assert len(report.recommendations) >= 1


# ===================================================================
# HealthReporter._generate_overall_recommendations
# ===================================================================


@pytest.mark.unit
class TestGenerateOverallRecommendations:
    """Test recommendation generation logic."""

    def test_unhealthy_adds_recommendation(self):
        reporter = HealthReporter()
        report = HealthReport()
        report.unhealthy_modules = 2
        result = _make_result("bad_mod", HealthStatus.UNHEALTHY, issues=["crash"])
        report.module_results["bad_mod"] = result
        reporter._generate_overall_recommendations(report)
        assert any("unhealthy" in r.lower() or "critical" in r.lower() for r in report.recommendations)

    def test_unknown_adds_recommendation(self):
        reporter = HealthReporter()
        report = HealthReport()
        report.unknown_modules = 3
        reporter._generate_overall_recommendations(report)
        assert any("unknown" in r.lower() or "investigate" in r.lower() for r in report.recommendations)

    def test_degraded_module_adds_recommendation(self):
        reporter = HealthReporter()
        report = HealthReport()
        result = _make_result("slow_mod", HealthStatus.DEGRADED)
        report.module_results["slow_mod"] = result
        reporter._generate_overall_recommendations(report)
        assert any("slow_mod" in r or "performance" in r.lower() for r in report.recommendations)

    def test_high_cpu_adds_recommendation(self):
        reporter = HealthReporter()
        report = HealthReport()
        report.system_metrics = {"cpu_percent": 90.0, "memory_percent": 50.0}
        reporter._generate_overall_recommendations(report)
        assert any("cpu" in r.lower() or "CPU" in r for r in report.recommendations)

    def test_high_memory_adds_recommendation(self):
        reporter = HealthReporter()
        report = HealthReport()
        report.system_metrics = {"cpu_percent": 10.0, "memory_percent": 95.0}
        reporter._generate_overall_recommendations(report)
        assert any("memory" in r.lower() for r in report.recommendations)

    def test_no_issues_no_extra_recommendations(self):
        reporter = HealthReporter()
        report = HealthReport()
        report.total_modules = 2
        report.healthy_modules = 2
        result1 = _make_result("mod1", HealthStatus.HEALTHY)
        result2 = _make_result("mod2", HealthStatus.HEALTHY)
        report.module_results["mod1"] = result1
        report.module_results["mod2"] = result2
        initial_len = len(report.recommendations)
        reporter._generate_overall_recommendations(report)
        # Healthy modules with no metrics produce no extra recommendations
        assert len(report.recommendations) == initial_len


# ===================================================================
# HealthReporter.format_health_report — all three formats
# ===================================================================


@pytest.mark.unit
class TestFormatHealthReportText:
    """Test format_health_report with text format."""

    def test_returns_string(self):
        reporter = HealthReporter()
        report = _make_healthy_report(2)
        result = reporter.format_health_report(report, format="text")
        assert isinstance(result, str)

    def test_contains_header(self):
        reporter = HealthReporter()
        report = _make_healthy_report()
        result = reporter.format_health_report(report, format="text")
        assert "Health Report" in result

    def test_contains_overall_status(self):
        reporter = HealthReporter()
        report = _make_healthy_report(3)
        result = reporter.format_health_report(report, format="text")
        assert "Overall Status" in result

    def test_contains_health_score(self):
        reporter = HealthReporter()
        report = _make_healthy_report(3)
        result = reporter.format_health_report(report, format="text")
        assert "Health Score" in result or "%" in result

    def test_contains_module_counts(self):
        reporter = HealthReporter()
        report = _make_healthy_report(4)
        result = reporter.format_health_report(report, format="text")
        assert "4" in result

    def test_contains_critical_issues_section_when_present(self):
        reporter = HealthReporter()
        report = HealthReport()
        report.critical_issues.append("Something is very broken")
        result = reporter.format_health_report(report, format="text")
        assert "Critical Issues" in result
        assert "Something is very broken" in result

    def test_contains_recommendations_section_when_present(self):
        reporter = HealthReporter()
        report = HealthReport()
        report.recommendations.append("Do this thing")
        result = reporter.format_health_report(report, format="text")
        assert "Recommendations" in result
        assert "Do this thing" in result

    def test_system_metrics_shown_when_present(self):
        reporter = HealthReporter()
        report = HealthReport()
        report.system_metrics = {"cpu_percent": 42.5}
        result = reporter.format_health_report(report, format="text")
        assert "System Metrics" in result
        assert "42.5" in result

    def test_default_format_is_text(self):
        reporter = HealthReporter()
        report = HealthReport()
        text_result = reporter.format_health_report(report, format="text")
        default_result = reporter.format_health_report(report)
        assert text_result == default_result


@pytest.mark.unit
class TestFormatHealthReportJson:
    """Test format_health_report with json format."""

    def test_returns_valid_json(self):
        reporter = HealthReporter()
        report = _make_healthy_report(2)
        result = reporter.format_health_report(report, format="json")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_json_has_all_fields(self):
        reporter = HealthReporter()
        report = _make_healthy_report(3)
        result = reporter.format_health_report(report, format="json")
        parsed = json.loads(result)
        assert "timestamp" in parsed
        assert "total_modules" in parsed
        assert "healthy_modules" in parsed
        assert "summary" in parsed

    def test_json_indented(self):
        reporter = HealthReporter()
        report = HealthReport()
        result = reporter.format_health_report(report, format="json")
        # indent=2 produces newlines
        assert "\n" in result


@pytest.mark.unit
class TestFormatHealthReportMarkdown:
    """Test format_health_report with markdown format."""

    def test_returns_string(self):
        reporter = HealthReporter()
        report = HealthReport()
        result = reporter.format_health_report(report, format="markdown")
        assert isinstance(result, str)

    def test_contains_h1_header(self):
        reporter = HealthReporter()
        report = HealthReport()
        result = reporter.format_health_report(report, format="markdown")
        assert "# Codomyrmex Health Report" in result

    def test_contains_bold_overall_status(self):
        reporter = HealthReporter()
        report = _make_healthy_report(2)
        result = reporter.format_health_report(report, format="markdown")
        assert "**Overall Status:**" in result

    def test_contains_module_summary_section(self):
        reporter = HealthReporter()
        report = _make_healthy_report(2)
        result = reporter.format_health_report(report, format="markdown")
        assert "## Module Status Summary" in result

    def test_contains_critical_issues_section_when_present(self):
        reporter = HealthReporter()
        report = HealthReport()
        report.critical_issues.append("critical error here")
        result = reporter.format_health_report(report, format="markdown")
        assert "## Critical Issues" in result
        assert "critical error here" in result

    def test_contains_recommendations_section_when_present(self):
        reporter = HealthReporter()
        report = HealthReport()
        report.recommendations.append("suggestion here")
        result = reporter.format_health_report(report, format="markdown")
        assert "## Recommendations" in result
        assert "suggestion here" in result

    def test_contains_module_details_section(self):
        reporter = HealthReporter()
        report = HealthReport()
        result = _make_result("core_mod", HealthStatus.DEGRADED, issues=["slow"])
        report.module_results["core_mod"] = result
        md = reporter.format_health_report(report, format="markdown")
        assert "### core_mod" in md
        assert "DEGRADED" in md

    def test_module_issues_listed_under_module(self):
        reporter = HealthReporter()
        report = HealthReport()
        result = _make_result("broken_mod", HealthStatus.UNHEALTHY, issues=["crash loop"])
        report.module_results["broken_mod"] = result
        md = reporter.format_health_report(report, format="markdown")
        assert "crash loop" in md

    def test_module_recommendations_listed(self):
        reporter = HealthReporter()
        report = HealthReport()
        result = HealthCheckResult(module_name="perf_mod", status=HealthStatus.DEGRADED)
        result.recommendations.append("reduce load")
        report.module_results["perf_mod"] = result
        md = reporter.format_health_report(report, format="markdown")
        assert "reduce load" in md


# ===================================================================
# HealthReporter.export_health_report
# ===================================================================


@pytest.mark.unit
class TestExportHealthReport:
    """Test HealthReporter.export_health_report file I/O."""

    def test_export_text_creates_file(self, tmp_path):
        reporter = HealthReporter()
        report = _make_healthy_report(2)
        filepath = str(tmp_path / "report.txt")
        reporter.export_health_report(report, filepath)
        assert Path(filepath).exists()

    def test_export_json_by_extension(self, tmp_path):
        reporter = HealthReporter()
        report = _make_healthy_report(2)
        filepath = str(tmp_path / "report.json")
        reporter.export_health_report(report, filepath)
        assert Path(filepath).exists()
        data = json.loads(Path(filepath).read_text())
        assert "timestamp" in data

    def test_export_markdown_by_extension(self, tmp_path):
        reporter = HealthReporter()
        report = _make_healthy_report(2)
        filepath = str(tmp_path / "report.md")
        reporter.export_health_report(report, filepath)
        assert Path(filepath).exists()
        content = Path(filepath).read_text()
        assert "# Codomyrmex Health Report" in content

    def test_export_explicit_json_format(self, tmp_path):
        reporter = HealthReporter()
        report = _make_healthy_report(2)
        filepath = str(tmp_path / "out.txt")
        reporter.export_health_report(report, filepath, format="json")
        data = json.loads(Path(filepath).read_text())
        assert "total_modules" in data

    def test_export_explicit_markdown_format(self, tmp_path):
        reporter = HealthReporter()
        report = HealthReport()
        filepath = str(tmp_path / "out.txt")
        reporter.export_health_report(report, filepath, format="markdown")
        content = Path(filepath).read_text()
        assert "# Codomyrmex Health Report" in content

    def test_export_invalid_path_raises(self, tmp_path):
        reporter = HealthReporter()
        report = HealthReport()
        filepath = str(tmp_path / "nonexistent" / "deep" / "dir" / "report.txt")
        with pytest.raises(Exception):
            reporter.export_health_report(report, filepath)

    def test_exported_text_is_nonempty(self, tmp_path):
        reporter = HealthReporter()
        report = _make_healthy_report(3)
        filepath = str(tmp_path / "check.txt")
        reporter.export_health_report(report, filepath)
        content = Path(filepath).read_text()
        assert len(content) > 50


# ===================================================================
# HealthReporter.compare_health_reports
# ===================================================================


@pytest.mark.unit
class TestCompareHealthReports:
    """Test compare_health_reports diff logic."""

    def _two_reports(self):
        """Return (current, previous) pair of HealthReports with shared module."""
        prev = HealthReport()
        prev.total_modules = 2
        prev.healthy_modules = 2
        prev.module_results["mod_a"] = _make_result("mod_a", HealthStatus.HEALTHY)
        prev.module_results["mod_b"] = _make_result("mod_b", HealthStatus.HEALTHY)

        curr = HealthReport()
        curr.total_modules = 2
        curr.healthy_modules = 1
        curr.unhealthy_modules = 1
        curr.module_results["mod_a"] = _make_result("mod_a", HealthStatus.UNHEALTHY, issues=["disk full"])
        curr.module_results["mod_b"] = _make_result("mod_b", HealthStatus.HEALTHY)
        return curr, prev

    def test_returns_dict(self):
        reporter = HealthReporter()
        curr, prev = self._two_reports()
        comparison = reporter.compare_health_reports(curr, prev)
        assert isinstance(comparison, dict)

    def test_has_expected_keys(self):
        reporter = HealthReporter()
        curr, prev = self._two_reports()
        comparison = reporter.compare_health_reports(curr, prev)
        required_keys = {
            "timestamp_current",
            "timestamp_previous",
            "time_difference_seconds",
            "health_score_change",
            "status_changes",
            "new_issues",
            "resolved_issues",
            "new_modules",
            "removed_modules",
        }
        assert required_keys.issubset(comparison.keys())

    def test_status_change_detected(self):
        reporter = HealthReporter()
        curr, prev = self._two_reports()
        comparison = reporter.compare_health_reports(curr, prev)
        # mod_a changed from healthy -> unhealthy
        assert "mod_a" in comparison["status_changes"]
        assert comparison["status_changes"]["mod_a"]["from"] == "healthy"
        assert comparison["status_changes"]["mod_a"]["to"] == "unhealthy"

    def test_no_status_change_for_stable_module(self):
        reporter = HealthReporter()
        curr, prev = self._two_reports()
        comparison = reporter.compare_health_reports(curr, prev)
        # mod_b stayed healthy
        assert "mod_b" not in comparison["status_changes"]

    def test_health_score_change_is_numeric(self):
        reporter = HealthReporter()
        curr, prev = self._two_reports()
        comparison = reporter.compare_health_reports(curr, prev)
        assert isinstance(comparison["health_score_change"], float)

    def test_health_score_change_negative_when_worse(self):
        reporter = HealthReporter()
        curr, prev = self._two_reports()
        # prev is all healthy (100%), curr has one unhealthy (50%)
        comparison = reporter.compare_health_reports(curr, prev)
        assert comparison["health_score_change"] < 0

    def test_new_module_detected(self):
        reporter = HealthReporter()
        prev = HealthReport()
        prev.module_results["old"] = _make_result("old", HealthStatus.HEALTHY)

        curr = HealthReport()
        curr.module_results["old"] = _make_result("old", HealthStatus.HEALTHY)
        curr.module_results["new_mod"] = _make_result("new_mod", HealthStatus.HEALTHY)

        comparison = reporter.compare_health_reports(curr, prev)
        assert "new_mod" in comparison["new_modules"]

    def test_removed_module_detected(self):
        reporter = HealthReporter()
        prev = HealthReport()
        prev.module_results["existing"] = _make_result("existing", HealthStatus.HEALTHY)
        prev.module_results["gone"] = _make_result("gone", HealthStatus.HEALTHY)

        curr = HealthReport()
        curr.module_results["existing"] = _make_result("existing", HealthStatus.HEALTHY)

        comparison = reporter.compare_health_reports(curr, prev)
        assert "gone" in comparison["removed_modules"]

    def test_new_issues_detected(self):
        reporter = HealthReporter()
        prev = HealthReport()
        prev.module_results["m"] = _make_result("m", HealthStatus.HEALTHY)

        curr = HealthReport()
        curr.module_results["m"] = _make_result("m", HealthStatus.UNHEALTHY, issues=["new problem"])

        comparison = reporter.compare_health_reports(curr, prev)
        assert "new problem" in comparison["new_issues"]

    def test_resolved_issues_detected(self):
        reporter = HealthReporter()
        prev = HealthReport()
        prev.module_results["m"] = _make_result("m", HealthStatus.UNHEALTHY, issues=["old problem"])

        curr = HealthReport()
        curr.module_results["m"] = _make_result("m", HealthStatus.HEALTHY)

        comparison = reporter.compare_health_reports(curr, prev)
        assert "old problem" in comparison["resolved_issues"]

    def test_time_difference_is_positive_for_newer_current(self):
        reporter = HealthReporter()
        prev = HealthReport()
        import time as _time
        _time.sleep(0.01)
        curr = HealthReport()
        comparison = reporter.compare_health_reports(curr, prev)
        assert comparison["time_difference_seconds"] > 0


# ===================================================================
# Module-level convenience functions
# ===================================================================


@pytest.mark.unit
class TestModuleLevelFunctions:
    """Test module-level convenience wrappers."""

    def test_generate_health_report_returns_health_report(self):
        # Use an empty module list so no HealthChecker calls needed
        report = generate_health_report([])
        assert isinstance(report, HealthReport)

    def test_format_health_report_text(self):
        report = HealthReport()
        result = format_health_report(report, format="text")
        assert isinstance(result, str)
        assert "Health Report" in result

    def test_format_health_report_json(self):
        report = HealthReport()
        result = format_health_report(report, format="json")
        parsed = json.loads(result)
        assert "timestamp" in parsed

    def test_format_health_report_markdown(self):
        report = HealthReport()
        result = format_health_report(report, format="markdown")
        assert "# Codomyrmex Health Report" in result

    def test_export_health_report_creates_file(self, tmp_path):
        report = _make_healthy_report(1)
        filepath = str(tmp_path / "convenience.json")
        export_health_report(report, filepath)
        assert Path(filepath).exists()
        data = json.loads(Path(filepath).read_text())
        assert "total_modules" in data


# ===================================================================
# HealthReport to_dict with module results that have issues/recommendations
# ===================================================================


@pytest.mark.unit
class TestHealthReportToDictWithResults:
    """Test to_dict serialisation when module_results contains real HealthCheckResults."""

    def test_module_result_status_serialised(self):
        report = HealthReport()
        report.module_results["x"] = _make_result("x", HealthStatus.DEGRADED)
        d = report.to_dict()
        assert d["module_results"]["x"]["status"] == "degraded"

    def test_module_result_issues_serialised(self):
        report = HealthReport()
        result = _make_result("y", HealthStatus.UNHEALTHY, issues=["something bad"])
        report.module_results["y"] = result
        d = report.to_dict()
        assert "something bad" in d["module_results"]["y"]["issues"]

    def test_issues_count_in_summary_matches(self):
        report = HealthReport()
        result = _make_result("z", HealthStatus.UNHEALTHY, issues=["e1", "e2", "e3"])
        report.module_results["z"] = result
        d = report.to_dict()
        assert d["summary"]["issues_count"] >= 3
