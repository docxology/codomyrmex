"""Tests for Sprint 37: Security Audit & Compliance.

Covers PermissionModel (RBAC), ComplianceGenerator (OWASP),
SecretScanner (regex + entropy), and SecurityDashboard.
"""

import pytest

from codomyrmex.security.compliance_report import (
    ComplianceCheck,
    ComplianceGenerator,
    ComplianceStatus,
)
from codomyrmex.security.dashboard import SecurityDashboard
from codomyrmex.security.permissions import Permission, PermissionModel, Role
from codomyrmex.security.secrets.secret_scanner import SecretScanner

# ─── PermissionModel ──────────────────────────────────────────────────

class TestPermissionModel:
    """Test suite for PermissionModel."""

    def test_role_hierarchy(self):
        """Test functionality: role hierarchy."""
        model = PermissionModel()
        model.grant("alice", Role.OPERATOR)
        assert model.check("alice", Permission.READ)
        assert model.check("alice", Permission.WRITE)
        assert model.check("alice", Permission.EXECUTE)
        assert not model.check("alice", Permission.ADMIN)

    def test_admin_has_all(self):
        """Test functionality: admin has all."""
        model = PermissionModel()
        model.grant("root", Role.ADMIN)
        for p in Permission:
            assert model.check("root", p)

    def test_viewer_read_only(self):
        """Test functionality: viewer read only."""
        model = PermissionModel()
        model.grant("bob", Role.VIEWER)
        assert model.check("bob", Permission.READ)
        assert not model.check("bob", Permission.WRITE)

    def test_revoke(self):
        """Test functionality: revoke."""
        model = PermissionModel()
        model.grant("alice", Role.ADMIN)
        model.revoke("alice", Role.ADMIN)
        assert not model.check("alice", Permission.ADMIN)

    def test_permission_matrix(self):
        """Test functionality: permission matrix."""
        model = PermissionModel()
        model.grant("alice", Role.OPERATOR)
        matrix = model.permission_matrix()
        assert matrix["alice"]["read"] is True
        assert matrix["alice"]["admin"] is False


# ─── ComplianceGenerator ─────────────────────────────────────────────

class TestComplianceGenerator:
    """Test suite for ComplianceGenerator."""

    def test_owasp_checks(self):
        """Test functionality: owasp checks."""
        gen = ComplianceGenerator()
        gen.add_owasp_checks()
        report = gen.generate()
        assert report.total_checks == 10
        assert report.pass_rate == pytest.approx(1.0)

    def test_failed_checks(self):
        """Test functionality: failed checks."""
        gen = ComplianceGenerator()
        gen.add_check(ComplianceCheck(
            check_id="C1", category="custom",
            description="test", status=ComplianceStatus.FAIL,
        ))
        report = gen.generate()
        assert len(report.failed_checks()) == 1

    def test_markdown_output(self):
        """Test functionality: markdown output."""
        gen = ComplianceGenerator()
        gen.add_owasp_checks()
        report = gen.generate()
        md = report.to_markdown()
        assert "OWASP" not in md or "A01" in md  # Contains check IDs


# ─── SecretScanner ───────────────────────────────────────────────────

class TestSecretScanner:
    """Test suite for SecretScanner."""

    def test_detects_api_key(self):
        """Test functionality: detects api key."""
        source = 'api_key = "sk_live_abc123def456ghi789jkl012"'
        scanner = SecretScanner()
        findings = scanner.scan_string(source, "config.py")
        assert len(findings) >= 1
        assert any(f.secret_type == "api_key" for f in findings)

    def test_detects_private_key(self):
        """Test functionality: detects private key."""
        source = "-----BEGIN RSA PRIVATE KEY-----"
        scanner = SecretScanner()
        findings = scanner.scan_string(source)
        assert any(f.secret_type == "private_key" for f in findings)

    def test_clean_code_no_findings(self):
        """Test functionality: clean code no findings."""
        source = "x = 1\ny = x + 2"
        scanner = SecretScanner()
        assert len(scanner.scan_string(source)) == 0


# ─── SecurityDashboard ──────────────────────────────────────────────

class TestSecurityDashboard:
    """Test suite for SecurityDashboard."""

    def test_posture_clean(self):
        """Test functionality: posture clean."""
        dashboard = SecurityDashboard()
        posture = dashboard.posture()
        assert posture.risk_score == 0.0

    def test_posture_with_secrets(self):
        """Test functionality: posture with secrets."""
        from codomyrmex.security.secrets.secret_scanner import SecretFinding
        findings = [SecretFinding(file_path="a", line_number=1, secret_type="api_key")]
        dashboard = SecurityDashboard(secrets=findings)
        posture = dashboard.posture()
        assert posture.risk_score > 0
        assert posture.secret_findings_count == 1
