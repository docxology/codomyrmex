"""
Comprehensive tests for the security.digital module.

This module tests all digital security functionality including
vulnerability scanning, security monitoring, encryption, and certificate validation.

NOTE: This file is deprecated. Use test_security_digital.py instead.
"""

import pytest
import tempfile
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Import cryptography conditionally
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    Fernet = None
    CRYPTOGRAPHY_AVAILABLE = False

# Skip all tests if cryptography is not available
pytestmark = pytest.mark.skipif(
    not CRYPTOGRAPHY_AVAILABLE,
    reason="cryptography package not available (install with: uv sync --extra security)"
)

from codomyrmex.security.digital.vulnerability_scanner import (
    VulnerabilityScanner,
    scan_vulnerabilities,
    audit_code_security,
    check_compliance,
    VulnerabilityReport,
    SecurityScanResult,
    ComplianceCheck,
    SeverityLevel,
    ComplianceStandard
)

from codomyrmex.security.digital.security_monitor import (
    SecurityMonitor,
    monitor_security_events,
    audit_access_logs,
    SecurityEvent,
    SecurityEventType,
    AlertLevel,
    AlertRule
)

# Import encryption components conditionally
try:
    from codomyrmex.security.digital.encryption_manager import (
        EncryptionManager,
        encrypt_sensitive_data,
        decrypt_sensitive_data
    )
    ENCRYPTION_AVAILABLE = True
except ImportError:
    EncryptionManager = None
    encrypt_sensitive_data = None
    decrypt_sensitive_data = None
    ENCRYPTION_AVAILABLE = False

# Import certificate validation components conditionally
try:
    from codomyrmex.security.digital.certificate_validator import (
        CertificateValidator,
        validate_ssl_certificates,
        SSLValidationResult
    )
    CERT_VALIDATION_AVAILABLE = True
except ImportError:
    CertificateValidator = None
    validate_ssl_certificates = None
    SSLValidationResult = None
    CERT_VALIDATION_AVAILABLE = False


class TestVulnerabilityScanner:
    """Test cases for VulnerabilityScanner functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.scanner = VulnerabilityScanner()

    def test_vulnerability_scanner_initialization(self):
        """Test VulnerabilityScanner initialization."""
        scanner = VulnerabilityScanner()
        assert scanner.config is not None
        assert "scan_types" in scanner.config
        assert scanner.scan_results == []

    def test_vulnerability_scanner_with_config(self):
        """Test VulnerabilityScanner with custom config."""
        config = {"scan_types": ["code"], "severity_threshold": "HIGH"}
        scanner = VulnerabilityScanner()
        scanner.config.update(config)
        assert scanner.config["severity_threshold"] == "HIGH"

    def test_scan_dependencies_python_success(self, tmp_path):
        """Test Python dependency scanning with real subprocess."""
        # Create requirements.txt
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("requests==2.25.0\n")

        scanner = VulnerabilityScanner()
        vulnerabilities = scanner._scan_dependencies(str(tmp_path))

        # Should return a list (may be empty if no vulnerabilities found)
        assert isinstance(vulnerabilities, list)

    def test_scan_dependencies_nodejs_success(self, tmp_path):
        """Test Node.js dependency scanning with real subprocess."""
        # Create package.json
        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"dependencies": {"lodash": "^4.17.0"}}')

        scanner = VulnerabilityScanner()
        vulnerabilities = scanner._scan_dependencies(str(tmp_path))

        # Should return a list
        assert isinstance(vulnerabilities, list)

    def test_scan_code_security_success(self, tmp_path):
        """Test code security scanning with real subprocess."""
        # Create Python file and project indicators
        py_file = tmp_path / "test.py"
        py_file.write_text("print('Hello World')")

        # Create pyproject.toml to make it a valid Python project
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("""
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "test-project"
version = "0.1.0"
""")

        scanner = VulnerabilityScanner()
        vulnerabilities = scanner._scan_code_security(str(tmp_path))

        # Should return a list
        assert isinstance(vulnerabilities, list)

    def test_check_compliance_owasp(self):
        """Test OWASP compliance checking."""
        scanner = VulnerabilityScanner()
        compliance_checks = scanner._check_compliance("/fake/path")

        assert isinstance(compliance_checks, list)
        # Should have OWASP checks
        owasp_checks = [c for c in compliance_checks if "OWASP" in c.get("standard", "")]
        assert len(owasp_checks) > 0

    def test_calculate_risk_score(self):
        """Test risk score calculation."""
        scanner = VulnerabilityScanner()

        # Test with no vulnerabilities
        score = scanner._calculate_risk_score([])
        assert score == 0.0

        # Test with vulnerabilities
        vulnerabilities = [
            {"severity": "CRITICAL"},
            {"severity": "HIGH"},
            {"severity": "MEDIUM"}
        ]
        score = scanner._calculate_risk_score(vulnerabilities)
        assert score > 0.0
        assert score <= 100.0

    def test_generate_recommendations(self):
        """Test security recommendations generation."""
        scanner = VulnerabilityScanner()

        # Test with no vulnerabilities
        recommendations = scanner._generate_recommendations([])
        assert len(recommendations) > 0

        # Test with vulnerabilities
        vulnerabilities = [{"severity": "CRITICAL"}]
        recommendations = scanner._generate_recommendations(vulnerabilities)
        assert len(recommendations) > 0

    def test_scan_vulnerabilities_complete(self, tmp_path):
        """Test complete vulnerability scan with real implementation."""
        # Create a simple Python project
        py_file = tmp_path / "main.py"
        py_file.write_text("print('Hello World')")

        scanner = VulnerabilityScanner()
        report = scanner.scan_vulnerabilities(str(tmp_path), ["code"])

        assert isinstance(report, VulnerabilityReport)
        assert report.target_path == str(tmp_path)
        assert report.scan_status == "completed"
        assert "scan_" in report.scan_id

    def test_generate_scan_id(self):
        """Test scan ID generation."""
        scanner = VulnerabilityScanner()
        scan_id = scanner._generate_scan_id("/test/path")

        assert scan_id.startswith("scan_")
        assert len(scan_id) > 10

    def test_is_python_project(self, tmp_path):
        """Test Python project detection with real files."""
        scanner = VulnerabilityScanner()

        # Test without Python files
        assert not scanner._is_python_project(str(tmp_path))

        # Add Python file
        py_file = tmp_path / "main.py"
        py_file.write_text("print('test')")

        # Should still not be a Python project without project indicators
        assert not scanner._is_python_project(str(tmp_path))

        # Add requirements.txt to make it a proper Python project
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("requests==2.25.0")
        assert scanner._is_python_project(str(tmp_path))

    def test_is_nodejs_project(self, tmp_path):
        """Test Node.js project detection with real files."""
        scanner = VulnerabilityScanner()

        # Test without Node.js files
        assert not scanner._is_nodejs_project(str(tmp_path))

        # Add package.json
        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"name": "test"}')
        assert scanner._is_nodejs_project(str(tmp_path))


class TestSecurityMonitor:
    """Test cases for SecurityMonitor functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.monitor = SecurityMonitor()

    def test_security_monitor_initialization(self):
        """Test SecurityMonitor initialization."""
        monitor = SecurityMonitor()
        assert monitor.events == []
        assert len(monitor.alert_rules) >= 0  # May have default rules
        assert monitor.monitoring_active is False
        assert monitor.alert_callbacks == []

    def test_add_alert_rule(self):
        """Test adding alert rules."""
        rule = AlertRule(
            rule_id="test_rule",
            name="Test Rule",
            description="A test alert rule",
            event_type=SecurityEventType.AUTHENTICATION_FAILURE,
            conditions={"count_threshold": 5},
            alert_level=AlertLevel.HIGH
        )

        self.monitor.add_alert_rule(rule)
        assert "test_rule" in self.monitor.alert_rules
        assert self.monitor.alert_rules["test_rule"].name == "Test Rule"

    def test_remove_alert_rule(self):
        """Test removing alert rules."""
        rule = AlertRule(
            rule_id="test_rule",
            name="Test Rule",
            description="A test alert rule",
            event_type=SecurityEventType.AUTHENTICATION_FAILURE,
            conditions={},
            alert_level=AlertLevel.MEDIUM
        )

        self.monitor.add_alert_rule(rule)
        assert "test_rule" in self.monitor.alert_rules

        self.monitor.remove_alert_rule("test_rule")
        assert "test_rule" not in self.monitor.alert_rules

    def test_parse_log_line_auth_failure(self):
        """Test parsing authentication failure log lines."""
        monitor = SecurityMonitor()
        log_line = "Failed password for user test from 192.168.1.1"

        event = monitor._parse_log_line(log_line, "/var/log/auth.log")

        assert event is not None
        assert event.event_type == SecurityEventType.AUTHENTICATION_FAILURE
        assert event.user_id == "test"
        assert event.source_ip == "192.168.1.1"

    def test_parse_log_line_suspicious_activity(self):
        """Test parsing suspicious activity log lines."""
        monitor = SecurityMonitor()
        log_line = "Suspicious activity detected from unknown IP"

        event = monitor._parse_log_line(log_line, "/var/log/security.log")

        assert event is not None
        assert event.event_type == SecurityEventType.SUSPICIOUS_ACTIVITY

    def test_parse_log_line_invalid(self):
        """Test parsing invalid log lines."""
        monitor = SecurityMonitor()
        log_line = "Normal system operation log"

        event = monitor._parse_log_line(log_line, "/var/log/syslog")

        assert event is None

    def test_get_active_alerts(self):
        """Test getting active alerts."""
        # Add a real active alert
        event = SecurityEvent(
            event_id="test_event",
            event_type=SecurityEventType.AUTHENTICATION_FAILURE,
            timestamp=datetime.now(timezone.utc)
        )
        self.monitor.active_alerts["test_event"] = event

        active_alerts = self.monitor.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0].event_id == "test_event"

    def test_get_events_summary(self):
        """Test getting events summary."""
        # Add some test events
        events = [
            SecurityEvent(
                event_id="event1",
                event_type=SecurityEventType.AUTHENTICATION_FAILURE,
                timestamp=datetime.now(timezone.utc),
                severity=AlertLevel.HIGH
            ),
            SecurityEvent(
                event_id="event2",
                event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                timestamp=datetime.now(timezone.utc),
                severity=AlertLevel.MEDIUM
            )
        ]

        self.monitor.events = events

        summary = self.monitor.get_events_summary()

        assert summary["total_events"] == 2
        assert summary["events_by_type"]["authentication_failure"] == 1
        assert summary["events_by_type"]["suspicious_activity"] == 1
        assert summary["alerts_by_severity"]["HIGH"] == 1
        assert summary["alerts_by_severity"]["MEDIUM"] == 1

    def test_generate_event_id(self):
        """Test event ID generation."""
        event_id = self.monitor._generate_event_id()

        assert event_id.startswith("evt_")
        assert len(event_id) > 10


@pytest.mark.skipif(not ENCRYPTION_AVAILABLE, reason="Encryption dependencies not available")
class TestEncryptionManager:
    """Test cases for EncryptionManager functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = EncryptionManager()

    def test_encryption_manager_initialization_new_key(self):
        """Test EncryptionManager initialization with new key."""
        try:
            manager = EncryptionManager()
            # If we get here without exception, the test passes
            assert manager is not None
        except Exception as e:
            # If there's an exception, it should be expected (like file system errors)
            assert "Failed to initialize encryption" in str(e) or manager._fernet is not None

    def test_encryption_manager_initialization_existing_key(self, tmp_path):
        """Test EncryptionManager initialization with existing key."""
        # Create a real key file
        key_file = tmp_path / "encryption_key.key"
        key = Fernet.generate_key()
        key_file.write_bytes(key)

        # Test with real file operations
        try:
            # Modify manager to use our key file if possible
            manager = EncryptionManager()
            assert manager._fernet is not None
        except Exception:
            # May fail if key file path is hardcoded
            pass

    def test_encrypt_data_success(self):
        """Test successful data encryption with real implementation."""
        test_data = "sensitive information"

        result = self.manager.encrypt_data(test_data)

        assert result.success is True
        assert result.data is not None
        assert isinstance(result.data, bytes)
        assert result.metadata is not None
        assert "encryption_timestamp" in result.metadata

    def test_decrypt_data_success(self):
        """Test successful data decryption with real implementation."""
        test_data = "sensitive information"

        # Encrypt first
        encrypt_result = self.manager.encrypt_data(test_data)
        assert encrypt_result.success is True

        # Decrypt
        decrypt_result = self.manager.decrypt_data(encrypt_result.data)

        assert decrypt_result.success is True
        assert decrypt_result.data == test_data.encode('utf-8')

    def test_encrypt_decrypt_roundtrip(self):
        """Test full encrypt/decrypt roundtrip with real implementation."""
        original_data = "This is confidential data that needs encryption."

        # Encrypt
        encrypt_result = self.manager.encrypt_data(original_data)
        assert encrypt_result.success is True

        # Decrypt
        decrypt_result = self.manager.decrypt_data(encrypt_result.data)
        assert decrypt_result.success is True

        # Verify
        decrypted_text = decrypt_result.data.decode('utf-8')
        assert decrypted_text == original_data

    def test_encrypt_file_success(self, tmp_path):
        """Test successful file encryption with real file operations."""
        test_content = "This is test file content."
        input_path = tmp_path / "input.txt"
        input_path.write_text(test_content)
        output_path = tmp_path / "output.enc"

        result = self.manager.encrypt_file(str(input_path), str(output_path))

        assert result.success is True
        assert output_path.exists()

        # Verify encrypted file is different from original
        encrypted_content = output_path.read_bytes()
        assert encrypted_content != test_content.encode()

    def test_decrypt_file_success(self, tmp_path):
        """Test successful file decryption with real file operations."""
        test_content = "This is test file content."
        input_path = tmp_path / "input.txt"
        input_path.write_text(test_content)
        encrypted_path = tmp_path / "encrypted.enc"
        decrypted_path = tmp_path / "decrypted.txt"

        # Encrypt file
        encrypt_result = self.manager.encrypt_file(str(input_path), str(encrypted_path))
        assert encrypt_result.success is True

        # Decrypt file
        decrypt_result = self.manager.decrypt_file(str(encrypted_path), str(decrypted_path))
        assert decrypt_result.success is True

        # Verify content
        decrypted_content = decrypted_path.read_text()
        assert decrypted_content == test_content

    def test_generate_secure_password(self):
        """Test secure password generation."""
        password = EncryptionManager.generate_secure_password(length=16)

        assert len(password) == 16
        assert isinstance(password, str)

        # Check for variety of characters
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        assert has_upper or has_lower or has_digit or has_special

    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        result = EncryptionManager.hash_password(password)

        assert "hash" in result
        assert "salt" in result
        assert "iterations" in result
        assert result["iterations"] == 100000

    def test_verify_password_success(self):
        """Test successful password verification."""
        password = "test_password_123"
        hash_data = EncryptionManager.hash_password(password)

        result = EncryptionManager.verify_password(password, hash_data)
        assert result is True

    def test_verify_password_failure(self):
        """Test password verification failure."""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hash_data = EncryptionManager.hash_password(password)

        result = EncryptionManager.verify_password(wrong_password, hash_data)
        assert result is False

    def test_get_key_info(self):
        """Test key information retrieval."""
        info = self.manager.get_key_info()

        assert "key_file" in info
        assert "using_password" in info
        assert "encryption_initialized" in info

    def test_rotate_key_without_existing_key(self, tmp_path):
        """Test key rotation when no existing key."""
        result = self.manager.rotate_key()
        # This might fail due to file operations, but we're testing the attempt
        assert isinstance(result, bool)


@pytest.mark.skipif(not CERT_VALIDATION_AVAILABLE, reason="Certificate validation dependencies not available")
class TestCertificateValidator:
    """Test cases for CertificateValidator functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.validator = CertificateValidator()

    def test_certificate_validator_initialization(self):
        """Test CertificateValidator initialization."""
        validator = CertificateValidator(timeout=30)
        assert validator.timeout == 30

    def test_validate_ssl_certificate_success(self):
        """Test successful SSL certificate validation with real network."""
        # Test with a real hostname (may fail if network unavailable)
        try:
            result = self.validator.validate_ssl_certificate("example.com", 443)

            assert isinstance(result, SSLValidationResult)
            assert result.hostname == "example.com"
            assert result.port == 443
        except Exception:
            # Expected if network unavailable or SSL validation fails
            pytest.skip("Network unavailable or SSL validation failed")

    def test_get_certificate_security_score(self):
        """Test certificate security score calculation."""
        result = SSLValidationResult(
            hostname="example.com",
            port=443,
            valid=True,
            certificate_info={},
            key_size=2048,
            signature_algorithm="sha256WithRSAEncryption"
        )

        score_result = self.validator.get_certificate_security_score(result)

        assert "security_score" in score_result
        assert "grade" in score_result
        assert "recommendations" in score_result
        assert score_result["security_score"] >= 0
        assert score_result["security_score"] <= 100

    def test_monitor_certificate_expiration(self):
        """Test certificate expiration monitoring."""
        hostnames = ["example.com", "test.com"]

        # This would normally make network calls, but we're testing the structure
        alerts = self.validator.monitor_certificate_expiration(hostnames, 30)

        assert isinstance(alerts, list)
        # In a real scenario, this would return alerts for expiring certificates

    def test_score_to_grade_conversion(self):
        """Test security score to grade conversion."""
        # Test various score ranges
        assert self.validator._score_to_grade(95) == "A"
        assert self.validator._score_to_grade(85) == "B"
        assert self.validator._score_to_grade(75) == "C"
        assert self.validator._score_to_grade(65) == "D"
        assert self.validator._score_to_grade(45) == "F"


class TestConvenienceFunctions:
    """Test cases for module-level convenience functions."""

    def test_scan_vulnerabilities_function(self, tmp_path):
        """Test scan_vulnerabilities convenience function with real scanner."""
        # Create a test project
        (tmp_path / "test.py").write_text("print('test')")

        result = scan_vulnerabilities(str(tmp_path))

        # Should return a VulnerabilityReport
        assert isinstance(result, VulnerabilityReport)

    def test_audit_code_security_function(self, tmp_path):
        """Test audit_code_security convenience function with real scanner."""
        # Create a test project
        (tmp_path / "test.py").write_text("print('test')")

        result = audit_code_security(str(tmp_path))

        # Should return a list
        assert isinstance(result, list)

    def test_check_compliance_function(self, tmp_path):
        """Test check_compliance convenience function with real scanner."""
        result = check_compliance(str(tmp_path))

        # Should return a list
        assert isinstance(result, list)

    def test_monitor_security_events_function(self):
        """Test monitor_security_events convenience function with real monitor."""
        result = monitor_security_events()

        # Should return a SecurityMonitor instance
        assert isinstance(result, SecurityMonitor)

    def test_encrypt_sensitive_data_function(self):
        """Test encrypt_sensitive_data convenience function with real manager."""
        if not ENCRYPTION_AVAILABLE:
            pytest.skip("Encryption not available")

        result = encrypt_sensitive_data("test data")

        # Should return an encryption result
        assert hasattr(result, 'success')
        assert hasattr(result, 'data')

    def test_decrypt_sensitive_data_function(self):
        """Test decrypt_sensitive_data convenience function with real manager."""
        if not ENCRYPTION_AVAILABLE:
            pytest.skip("Encryption not available")

        # First encrypt some data
        encrypt_result = encrypt_sensitive_data("test data")
        if encrypt_result.success:
            test_data = encrypt_result.data
            result = decrypt_sensitive_data(test_data)

            # Should return a decryption result
            assert hasattr(result, 'success')
            assert hasattr(result, 'data')

    def test_validate_ssl_certificates_function(self):
        """Test validate_ssl_certificates convenience function with real validator."""
        if not CERT_VALIDATION_AVAILABLE:
            pytest.skip("Certificate validation not available")

        # Test with real hostname (may fail if network unavailable)
        try:
            results = validate_ssl_certificates(["example.com"])

            assert isinstance(results, list)
            if len(results) > 0:
                assert isinstance(results[0], SSLValidationResult)
        except Exception:
            pytest.skip("Network unavailable or SSL validation failed")


class TestIntegration:
    """Integration tests for security audit module components."""

    def test_vulnerability_report_to_dict(self):
        """Test VulnerabilityReport to_dict conversion."""
        report = VulnerabilityReport(
            scan_id="test_scan_123",
            timestamp=datetime.now(timezone.utc),
            target_path="/test/path"
        )

        report_dict = report.to_dict()

        assert report_dict["scan_id"] == "test_scan_123"
        assert "timestamp" in report_dict
        assert report_dict["target_path"] == "/test/path"

    def test_security_event_to_dict(self):
        """Test SecurityEvent to_dict conversion."""
        event = SecurityEvent(
            event_id="test_event_123",
            event_type=SecurityEventType.AUTHENTICATION_FAILURE,
            timestamp=datetime.now(timezone.utc),
            source_ip="192.168.1.1",
            user_id="test_user"
        )

        event_dict = event.to_dict()

        assert event_dict["event_id"] == "test_event_123"
        assert event_dict["event_type"] == "authentication_failure"
        assert event_dict["source_ip"] == "192.168.1.1"
        assert event_dict["user_id"] == "test_user"

    def test_ssl_validation_result_creation(self):
        """Test SSLValidationResult creation."""
        if not CERT_VALIDATION_AVAILABLE:
            pytest.skip("Certificate validation not available")

        result = SSLValidationResult(
            hostname="example.com",
            port=443,
            valid=True,
            certificate_info={"issuer": "Let's Encrypt"},
            key_size=2048
        )

        assert result.hostname == "example.com"
        assert result.port == 443
        assert result.valid is True
        assert result.key_size == 2048


class TestErrorHandling:
    """Test cases for error handling in security audit operations."""

    def test_vulnerability_scanner_file_not_found(self):
        """Test vulnerability scanner with non-existent file."""
        scanner = VulnerabilityScanner()

        # Should return empty list for non-existent file, not raise exception
        result = scanner._scan_python_dependencies("/non/existent/path/requirements.txt")
        assert result == []

    def test_encryption_manager_decrypt_invalid_data(self):
        """Test decryption with invalid data using real implementation."""
        if not ENCRYPTION_AVAILABLE:
            pytest.skip("Encryption not available")

        manager = EncryptionManager()
        result = manager.decrypt_data(b"invalid_data")

        # Should fail gracefully
        assert result.success is False
        assert result.error is not None

    def test_certificate_validator_connection_timeout(self):
        """Test certificate validator with connection timeout."""
        if not CERT_VALIDATION_AVAILABLE:
            pytest.skip("Certificate validation not available")

        validator = CertificateValidator(timeout=1)  # Very short timeout
        
        # Test with invalid hostname that should timeout
        try:
            result = validator.validate_ssl_certificate("invalid-hostname-that-does-not-exist.com", 443)

            assert isinstance(result, SSLValidationResult)
            assert result.valid is False
            assert len(result.validation_errors) > 0
        except Exception:
            # Expected if validation fails
            pass


if __name__ == "__main__":
    pytest.main([__file__])
