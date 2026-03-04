"""Tests for security/compliance_report.py — ComplianceReport and ComplianceGenerator."""

import pytest

from codomyrmex.security.compliance_report import (
    ComplianceCheck,
    ComplianceGenerator,
    ComplianceReport,
    ComplianceStatus,
)


class TestComplianceStatus:
    """Tests for the ComplianceStatus enum."""

    def test_all_statuses_present(self):
        """All four statuses exist."""
        statuses = {s.value for s in ComplianceStatus}
        assert "pass" in statuses
        assert "fail" in statuses
        assert "warn" in statuses
        assert "skip" in statuses

    def test_status_values(self):
        """Enum values match expected strings."""
        assert ComplianceStatus.PASS.value == "pass"
        assert ComplianceStatus.FAIL.value == "fail"
        assert ComplianceStatus.WARN.value == "warn"
        assert ComplianceStatus.SKIP.value == "skip"


class TestComplianceCheck:
    """Tests for the ComplianceCheck dataclass."""

    def test_create_minimal(self):
        """ComplianceCheck created with required fields only."""
        check = ComplianceCheck(
            check_id="C001",
            category="owasp",
            description="Verify access control",
        )
        assert check.check_id == "C001"
        assert check.category == "owasp"
        assert check.status == ComplianceStatus.SKIP  # default

    def test_create_with_status(self):
        """ComplianceCheck stores specified status."""
        check = ComplianceCheck(
            check_id="C002",
            category="dependency",
            description="Scan deps",
            status=ComplianceStatus.FAIL,
            severity="high",
        )
        assert check.status == ComplianceStatus.FAIL
        assert check.severity == "high"

    def test_default_severity(self):
        """Default severity is 'medium'."""
        check = ComplianceCheck("C003", "cat", "desc")
        assert check.severity == "medium"


class TestComplianceReport:
    """Tests for the ComplianceReport dataclass."""

    def test_empty_report_defaults(self):
        """Empty report has zero counts and zero pass rate."""
        report = ComplianceReport()
        assert report.total_checks == 0
        assert report.pass_rate == 0.0

    def test_total_checks_property(self):
        """total_checks equals number of checks added."""
        report = ComplianceReport()
        report.add_check(ComplianceCheck("C1", "cat", "desc", ComplianceStatus.PASS))
        report.add_check(ComplianceCheck("C2", "cat", "desc", ComplianceStatus.FAIL))
        assert report.total_checks == 2

    def test_pass_rate_all_pass(self):
        """pass_rate is 1.0 when all checks pass."""
        report = ComplianceReport()
        for i in range(4):
            report.add_check(ComplianceCheck(f"C{i}", "cat", "desc", ComplianceStatus.PASS))
        assert report.pass_rate == pytest.approx(1.0)

    def test_pass_rate_mixed(self):
        """pass_rate is fraction of passing checks."""
        report = ComplianceReport()
        report.add_check(ComplianceCheck("C1", "cat", "desc", ComplianceStatus.PASS))
        report.add_check(ComplianceCheck("C2", "cat", "desc", ComplianceStatus.FAIL))
        report.add_check(ComplianceCheck("C3", "cat", "desc", ComplianceStatus.PASS))
        report.add_check(ComplianceCheck("C4", "cat", "desc", ComplianceStatus.FAIL))
        assert report.pass_rate == pytest.approx(0.5)

    def test_pass_rate_all_fail(self):
        """pass_rate is 0.0 when all checks fail."""
        report = ComplianceReport()
        report.add_check(ComplianceCheck("C1", "cat", "desc", ComplianceStatus.FAIL))
        assert report.pass_rate == 0.0

    def test_failed_checks_filters(self):
        """failed_checks() returns only FAIL status checks."""
        report = ComplianceReport()
        report.add_check(ComplianceCheck("C1", "cat", "desc", ComplianceStatus.PASS))
        report.add_check(ComplianceCheck("C2", "cat", "desc", ComplianceStatus.FAIL))
        report.add_check(ComplianceCheck("C3", "cat", "desc", ComplianceStatus.FAIL))
        failed = report.failed_checks()
        assert len(failed) == 2
        assert all(c.status == ComplianceStatus.FAIL for c in failed)

    def test_by_category_filters(self):
        """by_category() returns only checks matching the category."""
        report = ComplianceReport()
        report.add_check(ComplianceCheck("C1", "owasp", "desc"))
        report.add_check(ComplianceCheck("C2", "dependency", "desc"))
        report.add_check(ComplianceCheck("C3", "owasp", "desc"))
        owasp = report.by_category("owasp")
        assert len(owasp) == 2
        assert all(c.category == "owasp" for c in owasp)

    def test_by_category_no_match(self):
        """by_category() returns empty list for unknown category."""
        report = ComplianceReport()
        report.add_check(ComplianceCheck("C1", "owasp", "desc"))
        assert report.by_category("unknown") == []

    def test_compute_summary_counts(self):
        """compute_summary() returns dict with correct counts."""
        report = ComplianceReport()
        report.add_check(ComplianceCheck("C1", "cat", "desc", ComplianceStatus.PASS))
        report.add_check(ComplianceCheck("C2", "cat", "desc", ComplianceStatus.FAIL))
        report.add_check(ComplianceCheck("C3", "cat", "desc", ComplianceStatus.WARN))
        summary = report.compute_summary()
        assert summary["pass"] == 1
        assert summary["fail"] == 1
        assert summary["warn"] == 1
        assert summary["skip"] == 0

    def test_compute_summary_sets_summary_attr(self):
        """compute_summary() stores result on the report itself."""
        report = ComplianceReport()
        report.add_check(ComplianceCheck("C1", "cat", "desc", ComplianceStatus.PASS))
        report.compute_summary()
        assert report.summary["pass"] == 1

    def test_to_markdown_contains_title(self):
        """to_markdown() output starts with # title."""
        report = ComplianceReport(title="My Compliance")
        report.add_check(ComplianceCheck("C1", "owasp", "desc", ComplianceStatus.PASS))
        md = report.to_markdown()
        assert "# My Compliance" in md

    def test_to_markdown_contains_table(self):
        """to_markdown() includes a markdown table with check rows."""
        report = ComplianceReport()
        report.add_check(ComplianceCheck("A01", "owasp", "Access control", ComplianceStatus.PASS))
        md = report.to_markdown()
        assert "| Check |" in md
        assert "A01" in md

    def test_to_markdown_contains_pass_rate(self):
        """to_markdown() includes Pass Rate percentage."""
        report = ComplianceReport()
        report.add_check(ComplianceCheck("C1", "cat", "desc", ComplianceStatus.PASS))
        md = report.to_markdown()
        assert "Pass Rate" in md

    def test_to_markdown_fail_icon(self):
        """to_markdown() uses fail icon for FAIL status."""
        report = ComplianceReport()
        report.add_check(ComplianceCheck("C1", "cat", "desc", ComplianceStatus.FAIL))
        md = report.to_markdown()
        assert "fail" in md.lower()

    def test_add_check_method(self):
        """add_check() appends to the checks list."""
        report = ComplianceReport()
        assert report.total_checks == 0
        report.add_check(ComplianceCheck("C1", "owasp", "desc"))
        assert report.total_checks == 1


class TestComplianceGenerator:
    """Tests for the ComplianceGenerator class."""

    def test_add_owasp_checks_count(self):
        """add_owasp_checks() adds exactly 10 OWASP checks."""
        gen = ComplianceGenerator()
        gen.add_owasp_checks()
        report = gen.generate()
        assert report.total_checks == 10

    def test_add_owasp_checks_category(self):
        """All OWASP checks have category 'owasp'."""
        gen = ComplianceGenerator()
        gen.add_owasp_checks()
        report = gen.generate()
        assert all(c.category == "owasp" for c in report.checks)

    def test_add_owasp_checks_default_status_pass(self):
        """Default status for OWASP checks is PASS."""
        gen = ComplianceGenerator()
        gen.add_owasp_checks()  # default_status=PASS
        report = gen.generate()
        assert all(c.status == ComplianceStatus.PASS for c in report.checks)

    def test_add_owasp_checks_fail_status(self):
        """OWASP checks can be added with FAIL status."""
        gen = ComplianceGenerator()
        gen.add_owasp_checks(default_status=ComplianceStatus.FAIL)
        report = gen.generate()
        assert all(c.status == ComplianceStatus.FAIL for c in report.checks)

    def test_generate_custom_title(self):
        """generate() uses the provided title."""
        gen = ComplianceGenerator()
        report = gen.generate(title="Q1 2026 Audit")
        assert report.title == "Q1 2026 Audit"

    def test_add_custom_check(self):
        """add_check() adds a custom check to the generator."""
        gen = ComplianceGenerator()
        check = ComplianceCheck(
            check_id="CUSTOM001",
            category="internal",
            description="Custom policy",
            status=ComplianceStatus.PASS,
        )
        gen.add_check(check)
        report = gen.generate()
        assert report.total_checks == 1
        assert report.checks[0].check_id == "CUSTOM001"

    def test_generate_with_owasp_and_custom(self):
        """Generator combines OWASP and custom checks."""
        gen = ComplianceGenerator()
        gen.add_owasp_checks()
        gen.add_check(ComplianceCheck("CUSTOM001", "internal", "desc"))
        report = gen.generate()
        assert report.total_checks == 11

    def test_generate_computes_summary(self):
        """generate() calls compute_summary on the report."""
        gen = ComplianceGenerator()
        gen.add_owasp_checks()
        report = gen.generate()
        # Summary should be populated
        assert "pass" in report.summary
        assert report.summary["pass"] == 10

    def test_empty_generator_produces_empty_report(self):
        """Generator with no checks produces empty report."""
        gen = ComplianceGenerator()
        report = gen.generate()
        assert report.total_checks == 0
        assert report.pass_rate == 0.0
