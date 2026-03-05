"""Integration tests for security_audit.py — security + crypto + maintenance + system_discovery."""

import sys
from pathlib import Path

import pytest

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use the test_project directory as a safe path to audit
TEST_PROJECT_ROOT = str(Path(__file__).parent.parent)


class TestSecurityImports:
    """Verify codomyrmex.security imports used in security_audit."""

    def test_import_security_module(self):
        """codomyrmex.security module is importable."""
        import codomyrmex.security as security

        assert security is not None

    def test_import_security_submodules(self):
        """Security submodules (scanning, secrets, audit) are importable."""
        from codomyrmex.security import audit, scanning, secrets

        assert audit is not None
        assert scanning is not None
        assert secrets is not None

    def test_digital_security_optional(self):
        """Digital security backend presence is detectable."""
        from src.security_audit import HAS_DIGITAL_SECURITY

        assert isinstance(HAS_DIGITAL_SECURITY, bool)


class TestCryptoImports:
    """Verify codomyrmex.crypto imports used in security_audit."""

    def test_import_crypto_module(self):
        """codomyrmex.crypto top-level is importable."""
        import codomyrmex.crypto as crypto

        assert crypto is not None

    def test_import_crypto_graphy_hashing(self):
        """crypto.graphy.hashing submodule is importable."""
        from codomyrmex.crypto.graphy import hashing

        assert hashing is not None

    def test_import_hash_data(self):
        """hash_data function is importable from crypto.graphy.hashing."""
        from codomyrmex.crypto.graphy.hashing import hash_data

        assert callable(hash_data)

    def test_import_verify_hash(self):
        """verify_hash function is importable from crypto.graphy.hashing."""
        from codomyrmex.crypto.graphy.hashing import verify_hash

        assert callable(verify_hash)

    def test_hash_data_produces_hex_string(self):
        """hash_data(b'test', 'sha256') returns a hex string."""
        from codomyrmex.crypto.graphy.hashing import hash_data

        result = hash_data(b"test data", "sha256")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_verify_hash_round_trip(self):
        """verify_hash correctly verifies a hash produced by hash_data."""
        from codomyrmex.crypto.graphy.hashing import hash_data, verify_hash

        data = b"round trip verification test"
        digest = hash_data(data, "sha256")
        assert verify_hash(data, digest, "sha256") is True


class TestMaintenanceImports:
    """Verify codomyrmex.maintenance imports used in security_audit."""

    def test_import_analyze_project_structure(self):
        """analyze_project_structure is importable and callable."""
        from codomyrmex.maintenance import analyze_project_structure

        assert callable(analyze_project_structure)

    def test_import_check_dependencies(self):
        """check_dependencies is importable and callable."""
        from codomyrmex.maintenance import check_dependencies

        assert callable(check_dependencies)


class TestSystemDiscoveryImports:
    """Verify codomyrmex.system_discovery imports used in security_audit."""

    def test_import_system_discovery(self):
        """SystemDiscovery is importable and constructable."""
        from codomyrmex.system_discovery import SystemDiscovery

        discovery = SystemDiscovery()
        assert discovery is not None

    def test_import_capability_scanner(self):
        """CapabilityScanner is importable and constructable."""
        from codomyrmex.system_discovery import CapabilityScanner

        scanner = CapabilityScanner()
        assert scanner is not None

    def test_import_health_checker(self):
        """HealthChecker is importable."""
        from codomyrmex.system_discovery import HealthChecker

        assert HealthChecker is not None


class TestSecurityAuditModule:
    """Functional tests for SecurityAudit class."""

    def test_has_security_modules_flag(self):
        """HAS_SECURITY_MODULES flag is True in security_audit.py."""
        from src.security_audit import HAS_SECURITY_MODULES

        assert HAS_SECURITY_MODULES is True

    def test_security_audit_instantiation(self):
        """SecurityAudit can be instantiated without errors."""
        from src.security_audit import SecurityAudit

        auditor = SecurityAudit()
        assert auditor is not None
        assert auditor.discovery is not None
        assert auditor.scanner is not None

    def test_hash_and_verify_bytes(self):
        """hash_and_verify() with bytes returns correct structure."""
        from src.security_audit import SecurityAudit

        auditor = SecurityAudit()
        result = auditor.hash_and_verify(b"test data", "sha256")
        assert isinstance(result, dict)
        assert result["verified"] is True
        assert result["algorithm"] == "sha256"
        assert isinstance(result["hex_digest"], str)
        assert result["data_length"] == 9

    def test_hash_and_verify_string(self):
        """hash_and_verify() with string auto-encodes to bytes."""
        from src.security_audit import SecurityAudit

        auditor = SecurityAudit()
        result = auditor.hash_and_verify("hello world", "sha256")
        assert result["verified"] is True
        assert result["data_length"] == 11

    def test_system_health_returns_dict(self):
        """system_health() returns dict with expected keys."""
        from src.security_audit import SecurityAudit

        auditor = SecurityAudit()
        result = auditor.system_health()
        assert isinstance(result, dict)
        assert "discovery_type" in result
        assert "scanner_type" in result
        assert "modules_found" in result
        assert isinstance(result["modules_found"], int)

    def test_audit_path_returns_dict(self):
        """audit_path() returns dict with expected keys."""
        from src.security_audit import SecurityAudit

        auditor = SecurityAudit()
        result = auditor.audit_path(TEST_PROJECT_ROOT)
        assert isinstance(result, dict)
        assert "path" in result
        assert "security_available" in result
        assert isinstance(result["security_available"], bool)

    def test_project_deps_returns_dict(self):
        """project_deps() returns dict with structure and dependencies keys."""
        from src.security_audit import SecurityAudit

        auditor = SecurityAudit()
        result = auditor.project_deps(TEST_PROJECT_ROOT)
        assert isinstance(result, dict)
        assert "structure" in result
        assert "dependencies" in result
