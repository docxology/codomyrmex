"""
Tests for Security Compliance Module
"""

import pytest

from codomyrmex.security.compliance import (
    SOC2_CONTROLS,
    ComplianceChecker,
    ComplianceFramework,
    ComplianceReport,
    Control,
    ControlResult,
    ControlStatus,
    PolicyChecker,
)


class TestControl:
    """Tests for Control."""

    def test_create(self):
        """Should create control."""
        control = Control(
            id="C1",
            title="Test Control",
            description="A test control",
            framework=ComplianceFramework.SOC2,
        )

        assert control.id == "C1"


class TestControlResult:
    """Tests for ControlResult."""

    def test_passed(self):
        """Should check passed status."""
        passed = ControlResult(control_id="C1", status=ControlStatus.PASSED)
        failed = ControlResult(control_id="C2", status=ControlStatus.FAILED)

        assert passed.passed
        assert not failed.passed


class TestComplianceReport:
    """Tests for ComplianceReport."""

    def test_scores(self):
        """Should calculate compliance score."""
        report = ComplianceReport(
            report_id="r1",
            framework=ComplianceFramework.SOC2,
        )
        report.results = [
            ControlResult("C1", ControlStatus.PASSED),
            ControlResult("C2", ControlStatus.PASSED),
            ControlResult("C3", ControlStatus.FAILED),
            ControlResult("C4", ControlStatus.FAILED),
        ]

        assert report.total_controls == 4
        assert report.passed_controls == 2
        assert report.failed_controls == 2
        assert report.compliance_score == 50.0


class TestPolicyChecker:
    """Tests for PolicyChecker."""

    def test_check_pass(self):
        """Should check passing condition."""
        checker = PolicyChecker(
            control_id="C1",
            check_fn=lambda ctx: ctx.get("has_policy"),
            pass_message="Policy exists",
        )

        result = checker.check({"has_policy": True})

        assert result.passed

    def test_check_fail(self):
        """Should check failing condition."""
        checker = PolicyChecker(
            control_id="C1",
            check_fn=lambda ctx: ctx.get("has_policy"),
            fail_message="No policy",
        )

        result = checker.check({"has_policy": False})

        assert not result.passed

    def test_check_exception(self):
        """Should handle exceptions."""
        checker = PolicyChecker(
            control_id="C1",
            check_fn=lambda ctx: ctx["missing_key"],
        )

        result = checker.check({})

        assert result.status == ControlStatus.UNKNOWN


class TestComplianceChecker:
    """Tests for ComplianceChecker."""

    def test_add_control(self):
        """Should add control."""
        checker = ComplianceChecker(ComplianceFramework.SOC2)
        checker.add_control(Control(
            id="C1",
            title="Test",
            description="",
            framework=ComplianceFramework.SOC2,
        ))

        assert checker.get_control("C1") is not None

    def test_assess(self):
        """Should run assessment."""
        checker = ComplianceChecker(ComplianceFramework.SOC2)
        checker.add_checker(PolicyChecker(
            control_id="C1",
            check_fn=lambda ctx: ctx.get("enabled"),
        ))
        checker.add_checker(PolicyChecker(
            control_id="C2",
            check_fn=lambda ctx: ctx.get("encrypted"),
        ))

        report = checker.assess({"enabled": True, "encrypted": False})

        assert report.passed_controls == 1
        assert report.failed_controls == 1

    def test_check_single(self):
        """Should check single control."""
        checker = ComplianceChecker(ComplianceFramework.GDPR)
        checker.add_checker(PolicyChecker(
            control_id="GDPR1",
            check_fn=lambda ctx: True,
        ))

        result = checker.check_control("GDPR1", {})

        assert result.passed


class TestSOC2Controls:
    """Tests for pre-built controls."""

    def test_soc2_controls_exist(self):
        """Should have pre-built SOC2 controls."""
        assert len(SOC2_CONTROLS) > 0
        assert all(c.framework == ComplianceFramework.SOC2 for c in SOC2_CONTROLS)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
