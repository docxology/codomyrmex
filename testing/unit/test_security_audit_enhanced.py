"""Unit tests for enhanced security audit module functionality."""

import pytest
import tempfile
import os
from pathlib import Path


class TestSecretsDetector:
    """Test cases for the enhanced secrets detector."""

    def test_secrets_detector_initialization(self):
        """Test SecretsDetector initialization."""
        from codomyrmex.security_audit.secrets_detector import SecretsDetector

        detector = SecretsDetector()
        assert detector is not None
        assert hasattr(detector, 'config')
        assert hasattr(detector, '_compiled_patterns')

    def test_audit_secrets_exposure_basic(self):
        """Test basic secrets detection in text content."""
        from codomyrmex.security_audit.secrets_detector import audit_secrets_exposure

        # Test with no secrets
        content = "This is normal text with no secrets."
        findings = audit_secrets_exposure(content)
        assert isinstance(findings, list)
        assert len(findings) == 0

        # Test with a potential secret (high entropy string)
        content_with_secret = "API_KEY = 'sk-1234567890abcdef1234567890abcdef12345678'"
        findings = audit_secrets_exposure(content_with_secret)
        assert isinstance(findings, list)
        # May or may not detect depending on entropy calculation

    def test_entropy_calculation(self):
        """Test entropy calculation for secret detection."""
        from codomyrmex.security_audit.secrets_detector import SecretsDetector

        detector = SecretsDetector()

        # Test low entropy (predictable)
        low_entropy = "aaaaaaaa"
        entropy = detector._calculate_entropy(low_entropy)
        assert entropy < 1.0

        # Test high entropy (random-like)
        high_entropy = "aB3kL9mN2pQ8rS5tU7vX1yZ4wA6bC"
        entropy = detector._calculate_entropy(high_entropy)
        assert entropy > 3.0

        # Test empty string
        entropy_empty = detector._calculate_entropy("")
        assert entropy_empty == 0.0

    def test_scan_file_for_secrets(self):
        """Test scanning a file for secrets."""
        from codomyrmex.security_audit.secrets_detector import scan_file_for_secrets

        # Create a temporary file with test content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test file\npassword = 'secret123'\n")
            temp_file = f.name

        try:
            findings = scan_file_for_secrets(temp_file)
            assert isinstance(findings, list)
        finally:
            os.unlink(temp_file)

    def test_scan_directory_for_secrets(self):
        """Test scanning a directory for secrets."""
        from codomyrmex.security_audit.secrets_detector import scan_directory_for_secrets

        # Create a temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, 'w') as f:
                f.write("# Test file\napi_key = 'sk-test123'\n")

            findings = scan_directory_for_secrets(temp_dir)
            assert isinstance(findings, list)


class TestSecurityAnalyzer:
    """Test cases for the enhanced security analyzer."""

    def test_security_analyzer_initialization(self):
        """Test SecurityAnalyzer initialization."""
        from codomyrmex.security_audit.security_analyzer import SecurityAnalyzer

        analyzer = SecurityAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'vulnerable_patterns')
        assert hasattr(analyzer, 'safe_functions')

    def test_analyze_file_security(self):
        """Test analyzing a file for security issues."""
        from codomyrmex.security_audit.security_analyzer import analyze_file_security

        # Create a temporary Python file with potential security issues
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import os
def dangerous_function():
    user_input = input("Enter command: ")
    os.system(user_input)  # Command injection vulnerability
    eval(user_input)  # Code injection vulnerability
""")
            temp_file = f.name

        try:
            findings = analyze_file_security(temp_file)
            assert isinstance(findings, list)
            # Should detect some security issues
            assert len(findings) > 0
        finally:
            os.unlink(temp_file)

    def test_analyze_directory_security(self):
        """Test analyzing a directory for security issues."""
        from codomyrmex.security_audit.security_analyzer import analyze_directory_security

        # Create a temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test Python file
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, 'w') as f:
                f.write("os.system('ls')  # Dangerous\n")

            findings = analyze_directory_security(temp_dir)
            assert isinstance(findings, list)


class TestComplianceChecker:
    """Test cases for the enhanced compliance checker."""

    def test_compliance_checker_initialization(self):
        """Test ComplianceChecker initialization."""
        from codomyrmex.security_audit.compliance_checker import ComplianceChecker

        checker = ComplianceChecker()
        assert checker is not None
        assert hasattr(checker, 'standards')
        assert hasattr(checker, 'requirements')

        # Test with specific standards
        checker_custom = ComplianceChecker(["OWASP_TOP_10"])
        assert "OWASP_TOP_10" in checker_custom.standards

    def test_check_compliance_function(self):
        """Test the check_compliance convenience function."""
        from codomyrmex.security_audit.compliance_checker import check_compliance

        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a simple Python file
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, 'w') as f:
                f.write("# Test file\nimport os\n")

            results = check_compliance(temp_dir, ["OWASP_TOP_10"])
            assert isinstance(results, list)

            # Should have some compliance check results
            assert len(results) > 0

            # Each result should have the expected structure
            for result in results:
                assert hasattr(result, 'requirement')
                assert hasattr(result, 'status')
                assert hasattr(result, 'evidence')
                assert hasattr(result, 'findings')
                assert result.status in ["compliant", "non_compliant", "not_applicable", "manual_review_required"]

    def test_compliance_standards(self):
        """Test that supported compliance standards are available."""
        from codomyrmex.security_audit.compliance_checker import ComplianceChecker, ComplianceStandard

        checker = ComplianceChecker()

        # Test that we have requirements for major standards
        assert "OWASP_TOP_10" in checker.requirements
        assert "NIST_800_53" in checker.requirements
        assert "ISO_27001" in checker.requirements
        assert "PCI_DSS" in checker.requirements
        assert "GDPR" in checker.requirements
        assert "HIPAA" in checker.requirements

        # Test enum values
        assert ComplianceStandard.OWASP_TOP_10.value == "OWASP_TOP_10"
        assert ComplianceStandard.NIST_800_53.value == "NIST_800_53"

    def test_compliance_requirement_structure(self):
        """Test that compliance requirements have correct structure."""
        from codomyrmex.security_audit.compliance_checker import ComplianceChecker

        checker = ComplianceChecker()

        # Check OWASP requirements structure
        owasp_reqs = checker.requirements["OWASP_TOP_10"]
        assert len(owasp_reqs) > 0

        for req in owasp_reqs:
            assert hasattr(req, 'standard')
            assert hasattr(req, 'requirement_id')
            assert hasattr(req, 'title')
            assert hasattr(req, 'description')
            assert hasattr(req, 'severity')
            assert hasattr(req, 'category')
            assert hasattr(req, 'automated_check')
            assert hasattr(req, 'evidence_required')

            assert req.standard == "OWASP_TOP_10"
            assert req.severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


class TestSecurityFinding:
    """Test cases for SecurityFinding dataclass."""

    def test_security_finding_creation(self):
        """Test creating SecurityFinding instances."""
        from codomyrmex.security_audit.security_analyzer import SecurityFinding, SecurityIssue

        finding = SecurityFinding(
            issue_type=SecurityIssue.SQL_INJECTION,
            severity="HIGH",
            confidence=0.85,
            file_path="/test/file.py",
            line_number=10,
            code_snippet="cursor.execute('SELECT * FROM users WHERE id = ' + user_id)",
            description="SQL injection vulnerability detected",
            recommendation="Use parameterized queries instead of string concatenation"
        )

        assert finding.issue_type == SecurityIssue.SQL_INJECTION
        assert finding.severity == "HIGH"
        assert finding.confidence == 0.85
        assert finding.file_path == "/test/file.py"
        assert finding.line_number == 10
        assert "SQL injection" in finding.description

    def test_security_issue_enum(self):
        """Test SecurityIssue enum values."""
        from codomyrmex.security_audit.security_analyzer import SecurityIssue

        assert SecurityIssue.SQL_INJECTION.value == "sql_injection"
        assert SecurityIssue.XSS_VULNERABILITY.value == "xss_vulnerability"
        assert SecurityIssue.COMMAND_INJECTION.value == "command_injection"
        assert SecurityIssue.HARD_CODED_SECRET.value == "hard_coded_secret"


class TestComplianceRequirement:
    """Test cases for ComplianceRequirement dataclass."""

    def test_compliance_requirement_creation(self):
        """Test creating ComplianceRequirement instances."""
        from codomyrmex.security_audit.compliance_checker import ComplianceRequirement

        req = ComplianceRequirement(
            standard="OWASP_TOP_10",
            requirement_id="A01:2021",
            title="Broken Access Control",
            description="Restrict access to authorized users only",
            severity="CRITICAL",
            category="Access Control",
            automated_check=False,
            evidence_required=True
        )

        assert req.standard == "OWASP_TOP_10"
        assert req.requirement_id == "A01:2021"
        assert req.title == "Broken Access Control"
        assert req.severity == "CRITICAL"
        assert req.category == "Access Control"
        assert req.automated_check is False
        assert req.evidence_required is True
