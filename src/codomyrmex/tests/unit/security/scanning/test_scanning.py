"""
Tests for Security Scanning Module
"""

import pytest
import tempfile
from pathlib import Path
from codomyrmex.security.scanning import (
    Severity,
    FindingType,
    SecurityFinding,
    ScanResult,
    PatternRule,
    SQLInjectionRule,
    HardcodedSecretRule,
    CommandInjectionRule,
    InsecureRandomRule,
    SecurityScanner,
)


class TestSecurityFinding:
    """Tests for SecurityFinding."""
    
    def test_create(self):
        """Should create finding."""
        finding = SecurityFinding(
            id="f1",
            finding_type=FindingType.SQL_INJECTION,
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Potential SQL injection",
        )
        
        assert finding.severity == Severity.HIGH


class TestScanResult:
    """Tests for ScanResult."""
    
    def test_counts(self):
        """Should count findings."""
        result = ScanResult(scan_id="s1")
        result.findings = [
            SecurityFinding("f1", FindingType.SQL_INJECTION, Severity.CRITICAL, "", ""),
            SecurityFinding("f2", FindingType.XSS, Severity.HIGH, "", ""),
            SecurityFinding("f3", FindingType.EXPOSED_DEBUG, Severity.MEDIUM, "", ""),
        ]
        
        assert result.finding_count == 3
        assert result.critical_count == 1
        assert result.high_count == 1


class TestPatternRule:
    """Tests for PatternRule."""
    
    def test_match(self):
        """Should match patterns."""
        rule = PatternRule(
            rule_id="TEST001",
            finding_type=FindingType.EXPOSED_DEBUG,
            pattern=r"DEBUG\s*=\s*True",
            severity=Severity.MEDIUM,
            title="Debug Mode",
            description="Debug mode enabled",
        )
        
        findings = rule.check("DEBUG = True\nother code", "test.py")
        
        assert len(findings) == 1
        assert findings[0].line_number == 1


class TestSQLInjectionRule:
    """Tests for SQLInjectionRule."""
    
    def test_detect_format(self):
        """Should detect format string SQL."""
        rule = SQLInjectionRule()
        code = 'cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)'
        
        findings = rule.check(code, "app.py")
        
        assert len(findings) >= 1


class TestHardcodedSecretRule:
    """Tests for HardcodedSecretRule."""
    
    def test_detect_password(self):
        """Should detect hardcoded password."""
        rule = HardcodedSecretRule()
        code = 'password = "supersecret123"'
        
        findings = rule.check(code, "config.py")
        
        assert len(findings) == 1


class TestCommandInjectionRule:
    """Tests for CommandInjectionRule."""
    
    def test_detect_os_system(self):
        """Should detect os.system injection."""
        rule = CommandInjectionRule()
        code = 'os.system("ls " + user_input)'
        
        findings = rule.check(code, "utils.py")
        
        assert len(findings) == 1


class TestSecurityScanner:
    """Tests for SecurityScanner."""
    
    def test_scan_content(self):
        """Should scan content."""
        scanner = SecurityScanner()
        code = '''
password = "hardcoded123"
cursor.execute("SELECT * FROM users WHERE id = %s" % id)
'''
        
        findings = scanner.scan_content(code)
        
        assert len(findings) >= 2
    
    def test_scan_file(self):
        """Should scan file."""
        scanner = SecurityScanner()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('api_key = "secret12345678"\n')
            f.flush()
            
            result = scanner.scan_file(f.name)
        
        assert result.files_scanned == 1
        assert result.finding_count >= 1
    
    def test_scan_missing_file(self):
        """Should handle missing file."""
        scanner = SecurityScanner()
        result = scanner.scan_file("/nonexistent/path.py")
        
        assert len(result.errors) > 0
    
    def test_scan_directory(self):
        """Should scan directory."""
        scanner = SecurityScanner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            (Path(tmpdir) / "test.py").write_text('password = "test12345678"\n')
            
            result = scanner.scan_directory(tmpdir)
        
        assert result.files_scanned == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
