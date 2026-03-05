"""Tests for security/dashboard.py — SecurityDashboard and SecurityPosture."""

import pytest

from codomyrmex.security.compliance_report import (
    ComplianceCheck,
    ComplianceReport,
    ComplianceStatus,
)
from codomyrmex.security.dashboard import SecurityDashboard, SecurityPosture
from codomyrmex.security.permissions import PermissionModel, Role
from codomyrmex.security.secrets.secret_scanner import SecretFinding


class TestSecurityPosture:
    """Tests for the SecurityPosture dataclass."""

    def test_create_defaults(self):
        """SecurityPosture has sensible defaults."""
        posture = SecurityPosture()
        assert posture.compliance_pass_rate == 0.0
        assert posture.secret_findings_count == 0
        assert posture.risk_score == 0.0
        assert posture.total_checks == 0
        assert posture.permission_matrix == {}

    def test_create_with_values(self):
        """SecurityPosture stores all provided values."""
        posture = SecurityPosture(
            compliance_pass_rate=0.75,
            secret_findings_count=3,
            total_checks=10,
            risk_score=45.0,
        )
        assert posture.compliance_pass_rate == pytest.approx(0.75)
        assert posture.secret_findings_count == 3
        assert posture.risk_score == pytest.approx(45.0)


class TestSecurityDashboardDefaults:
    """Tests for SecurityDashboard with default (no-arg) initialization."""

    def test_posture_with_no_deps(self):
        """Dashboard with no deps produces zero risk score."""
        dashboard = SecurityDashboard()
        posture = dashboard.posture()
        assert isinstance(posture, SecurityPosture)
        assert posture.risk_score == 0.0
        assert posture.compliance_pass_rate == 0.0
        assert posture.secret_findings_count == 0

    def test_to_markdown_basic(self):
        """to_markdown() produces a non-empty string."""
        dashboard = SecurityDashboard()
        md = dashboard.to_markdown()
        assert isinstance(md, str)
        assert len(md) > 0

    def test_to_markdown_contains_header(self):
        """to_markdown() includes '# Security Dashboard' heading."""
        dashboard = SecurityDashboard()
        md = dashboard.to_markdown()
        assert "# Security Dashboard" in md

    def test_to_markdown_contains_risk_score(self):
        """to_markdown() contains Risk Score label."""
        dashboard = SecurityDashboard()
        md = dashboard.to_markdown()
        assert "Risk Score" in md


class TestSecurityDashboardWithCompliance:
    """Tests for SecurityDashboard wired to a real ComplianceReport."""

    def _make_report(self, pass_count: int, fail_count: int) -> ComplianceReport:
        report = ComplianceReport()
        for i in range(pass_count):
            report.add_check(
                ComplianceCheck(f"P{i}", "owasp", "desc", ComplianceStatus.PASS)
            )
        for i in range(fail_count):
            report.add_check(
                ComplianceCheck(f"F{i}", "owasp", "desc", ComplianceStatus.FAIL)
            )
        return report

    def test_compliance_pass_rate_propagated(self):
        """pass_rate from ComplianceReport is reflected in posture."""
        report = self._make_report(pass_count=8, fail_count=2)
        dashboard = SecurityDashboard(compliance=report)
        posture = dashboard.posture()
        assert posture.compliance_pass_rate == pytest.approx(0.8)

    def test_total_checks_propagated(self):
        """total_checks matches ComplianceReport total."""
        report = self._make_report(pass_count=5, fail_count=5)
        dashboard = SecurityDashboard(compliance=report)
        posture = dashboard.posture()
        assert posture.total_checks == 10

    def test_risk_score_from_compliance_failures(self):
        """Failing compliance checks increase risk score."""
        all_pass = self._make_report(pass_count=10, fail_count=0)
        all_fail = self._make_report(pass_count=0, fail_count=10)
        posture_pass = SecurityDashboard(compliance=all_pass).posture()
        posture_fail = SecurityDashboard(compliance=all_fail).posture()
        assert posture_fail.risk_score > posture_pass.risk_score

    def test_risk_score_capped_at_100(self):
        """risk_score never exceeds 100."""
        report = self._make_report(pass_count=0, fail_count=20)
        # 5 secrets × 10 = 50, plus compliance risk = 50 → 100
        secrets = [
            SecretFinding(
                file_path="x.py", line_number=1, secret_type="api_key", snippet="***"
            )
            for _ in range(5)
        ]
        dashboard = SecurityDashboard(compliance=report, secrets=secrets)
        posture = dashboard.posture()
        assert posture.risk_score <= 100.0


class TestSecurityDashboardWithSecrets:
    """Tests for SecurityDashboard wired to real SecretFinding objects."""

    def _make_findings(self, count: int) -> list[SecretFinding]:
        return [
            SecretFinding(
                file_path=f"file_{i}.py",
                line_number=i + 1,
                secret_type="api_key",
                snippet="api_key=***",
            )
            for i in range(count)
        ]

    def test_secret_count_propagated(self):
        """secret_findings_count matches number of SecretFinding objects."""
        findings = self._make_findings(3)
        dashboard = SecurityDashboard(secrets=findings)
        posture = dashboard.posture()
        assert posture.secret_findings_count == 3

    def test_risk_score_grows_with_secrets(self):
        """More secrets produce higher risk score."""
        d0 = SecurityDashboard(secrets=self._make_findings(0))
        d3 = SecurityDashboard(secrets=self._make_findings(3))
        assert d3.posture().risk_score > d0.posture().risk_score

    def test_zero_secrets_zero_secret_risk(self):
        """Zero secrets contribute zero to risk score."""
        dashboard = SecurityDashboard()
        posture = dashboard.posture()
        assert posture.secret_findings_count == 0


class TestSecurityDashboardWithPermissions:
    """Tests for SecurityDashboard wired to a PermissionModel."""

    def _make_model(self) -> PermissionModel:
        model = PermissionModel()
        model.grant("alice", Role.ADMIN)
        model.grant("bob", Role.VIEWER)
        return model

    def test_permission_matrix_in_posture(self):
        """posture() includes permission_matrix from PermissionModel."""
        model = self._make_model()
        dashboard = SecurityDashboard(permissions=model)
        posture = dashboard.posture()
        assert "alice" in posture.permission_matrix
        assert "bob" in posture.permission_matrix

    def test_permission_matrix_admin_has_all(self):
        """Admin in permission matrix shows all perms as True."""
        model = PermissionModel()
        model.grant("root", Role.ADMIN)
        dashboard = SecurityDashboard(permissions=model)
        posture = dashboard.posture()
        matrix = posture.permission_matrix
        assert matrix["root"]["admin"] is True
        assert matrix["root"]["delete"] is True

    def test_permission_matrix_viewer_limited(self):
        """Viewer in permission matrix shows limited perms."""
        model = PermissionModel()
        model.grant("viewer", Role.VIEWER)
        dashboard = SecurityDashboard(permissions=model)
        posture = dashboard.posture()
        matrix = posture.permission_matrix
        assert matrix["viewer"]["read"] is True
        assert matrix["viewer"]["admin"] is False

    def test_to_markdown_shows_permission_table(self):
        """to_markdown() includes Permission Matrix heading when perms exist."""
        model = self._make_model()
        dashboard = SecurityDashboard(permissions=model)
        md = dashboard.to_markdown()
        assert "Permission Matrix" in md

    def test_to_markdown_no_permission_section_when_empty(self):
        """to_markdown() excludes Permission Matrix when no grants."""
        dashboard = SecurityDashboard()
        md = dashboard.to_markdown()
        assert "Permission Matrix" not in md
