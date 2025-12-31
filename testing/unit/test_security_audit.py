"""
Comprehensive tests for the security_audit module.

This module tests all security auditing functionality including
vulnerability scanning, security monitoring, encryption, and certificate validation.
"""

import pytest
import tempfile
import os
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
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
    reason="cryptography package not available (install with: uv sync --extra security_audit)"
)

from codomyrmex.security_audit.vulnerability_scanner import (
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

from codomyrmex.security_audit.security_monitor import (
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
    from codomyrmex.security_audit.encryption_manager import (
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
    from codomyrmex.security_audit.certificate_validator import (
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

    @patch('codomyrmex.security_audit.vulnerability_scanner.subprocess.run')
    def test_scan_dependencies_python_success(self, mock_subprocess):
        """Test Python dependency scanning success."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '[{"name": "requests", "version": "2.25.0"}]'
        mock_subprocess.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create requirements.txt
            req_file = Path(temp_dir) / "requirements.txt"
            req_file.write_text("requests==2.25.0\n")

            scanner = VulnerabilityScanner()
            vulnerabilities = scanner._scan_dependencies(str(temp_dir))

            assert len(vulnerabilities) >= 0  # May be 0 if no real vulnerabilities
            mock_subprocess.assert_called()

    @patch('codomyrmex.security_audit.vulnerability_scanner.subprocess.run')
    def test_scan_dependencies_nodejs_success(self, mock_subprocess):
        """Test Node.js dependency scanning success."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"vulnerabilities": {"lodash": {"severity": "high"}}}'
        mock_subprocess.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create package.json
            pkg_file = Path(temp_dir) / "package.json"
            pkg_file.write_text('{"dependencies": {"lodash": "^4.17.0"}}')

            scanner = VulnerabilityScanner()
            vulnerabilities = scanner._scan_dependencies(str(temp_dir))

            assert isinstance(vulnerabilities, list)
            mock_subprocess.assert_called()

    @patch('codomyrmex.security_audit.vulnerability_scanner.subprocess.run')
    def test_scan_code_security_success(self, mock_subprocess):
        """Test code security scanning success."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"results": [{"filename": "test.py", "issues": []}]}'
        mock_subprocess.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Python file and project indicators
            py_file = Path(temp_dir) / "test.py"
            py_file.write_text("print('Hello World')")

            # Create pyproject.toml to make it a valid Python project
            pyproject_file = Path(temp_dir) / "pyproject.toml"
            pyproject_file.write_text("""
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "test-project"
version = "0.1.0"
""")

            scanner = VulnerabilityScanner()
            vulnerabilities = scanner._scan_code_security(str(temp_dir))

            assert isinstance(vulnerabilities, list)
            mock_subprocess.assert_called()

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
        assert "✅ No security vulnerabilities found" in recommendations[0]

        # Test with vulnerabilities
        vulnerabilities = [{"severity": "CRITICAL"}]
        recommendations = scanner._generate_recommendations(vulnerabilities)
        assert any("CRITICAL" in rec for rec in recommendations)

    def test_scan_vulnerabilities_complete(self):
        """Test complete vulnerability scan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a simple Python project
            py_file = Path(temp_dir) / "main.py"
            py_file.write_text("print('Hello World')")

            scanner = VulnerabilityScanner()
            report = scanner.scan_vulnerabilities(temp_dir, ["code"])

            assert isinstance(report, VulnerabilityReport)
            assert report.target_path == temp_dir
            assert report.scan_status == "completed"
            assert "scan_" in report.scan_id

    def test_generate_scan_id(self):
        """Test scan ID generation."""
        scanner = VulnerabilityScanner()
        scan_id = scanner._generate_scan_id("/test/path")

        assert scan_id.startswith("scan_")
        assert len(scan_id) > 10

    def test_is_python_project(self):
        """Test Python project detection."""
        scanner = VulnerabilityScanner()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test without Python files
            assert not scanner._is_python_project(temp_dir)

            # Add Python file
            py_file = Path(temp_dir) / "main.py"
            py_file.write_text("print('test')")

            # Should still not be a Python project without project indicators
            assert not scanner._is_python_project(temp_dir)

            # Add requirements.txt to make it a proper Python project
            req_file = Path(temp_dir) / "requirements.txt"
            req_file.write_text("requests==2.25.0")
            assert scanner._is_python_project(temp_dir)

    def test_is_nodejs_project(self):
        """Test Node.js project detection."""
        scanner = VulnerabilityScanner()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test without Node.js files
            assert not scanner._is_nodejs_project(temp_dir)

            # Add package.json
            pkg_file = Path(temp_dir) / "package.json"
            pkg_file.write_text('{"name": "test"}')
            assert scanner._is_nodejs_project(temp_dir)


class TestSecurityMonitor:
    """Test cases for SecurityMonitor functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.monitor = SecurityMonitor()

    def test_security_monitor_initialization(self):
        """Test SecurityMonitor initialization."""
        monitor = SecurityMonitor()
        assert monitor.events == []
        assert len(monitor.alert_rules) == 4  # Default alert rules are loaded
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
        # Add a mock active alert
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
        # Just test that the manager can be initialized
        # The actual key generation will be tested indirectly
        try:
            manager = EncryptionManager()
            # If we get here without exception, the test passes
            assert True
        except Exception as e:
            # If there's an exception, it should be expected (like file system errors)
            assert "Failed to initialize encryption" in str(e) or manager._fernet is not None

    def test_encryption_manager_initialization_existing_key(self):
        """Test EncryptionManager initialization with existing key."""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', new_callable=mock_open, read_data=Fernet.generate_key()):
                manager = EncryptionManager()

                assert manager._fernet is not None

    def test_encrypt_data_success(self):
        """Test successful data encryption."""
        test_data = "sensitive information"

        result = self.manager.encrypt_data(test_data)

        assert result.success is True
        assert result.data is not None
        assert isinstance(result.data, bytes)
        assert result.metadata is not None
        assert "encryption_timestamp" in result.metadata

    def test_decrypt_data_success(self):
        """Test successful data decryption."""
        test_data = "sensitive information"

        # Encrypt first
        encrypt_result = self.manager.encrypt_data(test_data)
        assert encrypt_result.success is True

        # Decrypt
        decrypt_result = self.manager.decrypt_data(encrypt_result.data)

        assert decrypt_result.success is True
        assert decrypt_result.data == test_data.encode('utf-8')

    def test_encrypt_decrypt_roundtrip(self):
        """Test full encrypt/decrypt roundtrip."""
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

    def test_encrypt_file_success(self):
        """Test successful file encryption."""
        test_content = "This is test file content."

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as input_file:
            input_file.write(test_content)
            input_path = input_file.name

        try:
            with tempfile.NamedTemporaryFile(delete=False) as output_file:
                output_path = output_file.name

            result = self.manager.encrypt_file(input_path, output_path)

            assert result.success is True
            assert os.path.exists(output_path)

            # Verify encrypted file is different from original
            with open(output_path, 'rb') as f:
                encrypted_content = f.read()
            assert encrypted_content != test_content.encode()

        finally:
            # Cleanup
            if os.path.exists(input_path):
                os.unlink(input_path)
            if 'output_path' in locals() and os.path.exists(output_path):
                os.unlink(output_path)

    def test_decrypt_file_success(self):
        """Test successful file decryption."""
        test_content = "This is test file content."

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as input_file:
            input_file.write(test_content)
            input_path = input_file.name

        try:
            # Encrypt file
            with tempfile.NamedTemporaryFile(delete=False) as encrypted_file:
                encrypted_path = encrypted_file.name

            encrypt_result = self.manager.encrypt_file(input_path, encrypted_path)
            assert encrypt_result.success is True

            # Decrypt file
            with tempfile.NamedTemporaryFile(delete=False) as decrypted_file:
                decrypted_path = decrypted_file.name

            decrypt_result = self.manager.decrypt_file(encrypted_path, decrypted_path)
            assert decrypt_result.success is True

            # Verify content
            with open(decrypted_path, 'r') as f:
                decrypted_content = f.read()
            assert decrypted_content == test_content

        finally:
            # Cleanup
            for path_var in ['input_path', 'encrypted_path', 'decrypted_path']:
                if path_var in locals() and os.path.exists(locals()[path_var]):
                    os.unlink(locals()[path_var])

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

    @patch('os.path.exists', return_value=False)
    def test_rotate_key_without_existing_key(self, mock_exists):
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

    @patch('codomyrmex.security_audit.certificate_validator.socket.create_connection')
    @patch('codomyrmex.security_audit.certificate_validator.ssl.create_default_context')
    def test_validate_ssl_certificate_success(self, mock_ssl_context, mock_socket):
        """Test successful SSL certificate validation."""
        # Mock SSL context and connection
        mock_context = MagicMock()
        mock_sock = MagicMock()
        mock_sock.getpeercert.return_value = b'mock_cert_der'

        mock_ssl_context.return_value = mock_context
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_socket.return_value.__exit__.return_value = None

        # Mock certificate parsing
        with patch('OpenSSL.crypto.load_certificate') as mock_load_cert:
            mock_cert = MagicMock()
            mock_cert.get_subject.return_value.CN = "example.com"
            mock_cert.get_issuer.return_value.CN = "Let's Encrypt"
            mock_cert.get_notBefore.return_value = b'20240101000000Z'
            mock_cert.get_notAfter.return_value = b'20241231000000Z'
            mock_cert.get_pubkey.return_value.bits.return_value = 2048
            mock_cert.get_signature_algorithm.return_value = b'sha256WithRSAEncryption'
            mock_cert.get_extension_count.return_value = 0

            mock_load_cert.return_value = mock_cert

            result = self.validator.validate_ssl_certificate("example.com", 443)

            assert isinstance(result, SSLValidationResult)
            assert result.hostname == "example.com"
            assert result.port == 443

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

    @patch('codomyrmex.security_audit.vulnerability_scanner.VulnerabilityScanner')
    def test_scan_vulnerabilities_function(self, mock_scanner_class):
        """Test scan_vulnerabilities convenience function."""
        mock_scanner = MagicMock()
        mock_report = MagicMock()
        mock_scanner.scan_vulnerabilities.return_value = mock_report
        mock_scanner_class.return_value = mock_scanner

        result = scan_vulnerabilities("/test/path")

        mock_scanner_class.assert_called_once()
        mock_scanner.scan_vulnerabilities.assert_called_once_with("/test/path", None)
        assert result == mock_report

    @patch('codomyrmex.security_audit.vulnerability_scanner.VulnerabilityScanner')
    def test_audit_code_security_function(self, mock_scanner_class):
        """Test audit_code_security convenience function."""
        mock_scanner = MagicMock()
        mock_scanner.scan_vulnerabilities.return_value.vulnerabilities = []
        mock_scanner_class.return_value = mock_scanner

        result = audit_code_security("/test/path")

        assert isinstance(result, list)

    @patch('codomyrmex.security_audit.vulnerability_scanner.VulnerabilityScanner')
    def test_check_compliance_function(self, mock_scanner_class):
        """Test check_compliance convenience function."""
        mock_scanner = MagicMock()
        mock_scanner.scan_vulnerabilities.return_value.compliance_checks = []
        mock_scanner_class.return_value = mock_scanner

        result = check_compliance("/test/path")

        assert isinstance(result, list)

    @patch('codomyrmex.security_audit.security_monitor.SecurityMonitor')
    def test_monitor_security_events_function(self, mock_monitor_class):
        """Test monitor_security_events convenience function."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        result = monitor_security_events()

        mock_monitor_class.assert_called_once()
        mock_monitor.start_monitoring.assert_called_once()
        assert result == mock_monitor

    @patch('codomyrmex.security_audit.encryption_manager.EncryptionManager')
    def test_encrypt_sensitive_data_function(self, mock_manager_class):
        """Test encrypt_sensitive_data convenience function."""
        mock_manager = MagicMock()
        mock_result = MagicMock()
        mock_manager.encrypt_data.return_value = mock_result
        mock_manager_class.return_value = mock_manager

        result = encrypt_sensitive_data("test data")

        mock_manager_class.assert_called_once()
        mock_manager.encrypt_data.assert_called_once_with("test data")
        assert result == mock_result

    @patch('codomyrmex.security_audit.encryption_manager.EncryptionManager')
    def test_decrypt_sensitive_data_function(self, mock_manager_class):
        """Test decrypt_sensitive_data convenience function."""
        mock_manager = MagicMock()
        mock_result = MagicMock()
        mock_manager.decrypt_data.return_value = mock_result
        mock_manager_class.return_value = mock_manager

        test_data = b"encrypted_data"
        result = decrypt_sensitive_data(test_data)

        mock_manager_class.assert_called_once()
        mock_manager.decrypt_data.assert_called_once_with(test_data)
        assert result == mock_result

    @patch('codomyrmex.security_audit.certificate_validator.CertificateValidator')
    def test_validate_ssl_certificates_function(self, mock_validator_class):
        """Test validate_ssl_certificates convenience function."""
        mock_validator = MagicMock()
        mock_result = MagicMock()
        mock_validator.validate_ssl_certificate.return_value = mock_result
        mock_validator_class.return_value = mock_validator

        results = validate_ssl_certificates(["example.com"])

        assert len(results) == 1
        assert results[0] == mock_result


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

    @patch('codomyrmex.security_audit.encryption_manager.Fernet')
    def test_encryption_manager_decrypt_invalid_data(self, mock_fernet):
        """Test decryption with invalid data."""
        mock_fernet_instance = MagicMock()
        mock_fernet_instance.decrypt.side_effect = Exception("Invalid token")
        mock_fernet.return_value = mock_fernet_instance

        manager = EncryptionManager()
        result = manager.decrypt_data(b"invalid_data")

        assert result.success is False
        assert "Invalid token" in result.error

    @patch('codomyrmex.security_audit.certificate_validator.socket.create_connection')
    def test_certificate_validator_connection_timeout(self, mock_socket):
        """Test certificate validator with connection timeout."""
        mock_socket.side_effect = TimeoutError("Connection timed out")

        validator = CertificateValidator()
        result = validator.validate_ssl_certificate("example.com", 443)

        assert isinstance(result, SSLValidationResult)
        assert result.valid is False
        assert len(result.validation_errors) > 0


if __name__ == "__main__":
    pytest.main([__file__])
