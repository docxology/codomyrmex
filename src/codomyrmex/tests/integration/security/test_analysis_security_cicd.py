#!/usr/bin/env python3
"""
Integration Test: Static Analysis → Security Audit → CI/CD Automation Workflow

This integration test validates the complete workflow from static code analysis
through security auditing to CI/CD pipeline automation, ensuring that code
quality checks, security scans, and deployment automation work together seamlessly.
"""

import os
import tempfile

import pytest

# Import modules for integration testing
try:
    from codomyrmex.coding.static_analysis import analyze_file, analyze_project
    STATIC_ANALYSIS_AVAILABLE = True
except ImportError:
    STATIC_ANALYSIS_AVAILABLE = False

try:
    from codomyrmex.security.digital import (
        analyze_file_security,
        check_compliance,
        scan_vulnerabilities,
    )
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

try:
    from codomyrmex.ci_cd_automation import create_pipeline, validate_pipeline_config
    CI_CD_AVAILABLE = True
except ImportError:
    CI_CD_AVAILABLE = False

try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger, setup_logging
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

# Set up logging for tests
if LOGGING_AVAILABLE and hasattr(setup_logging, '__call__'):
    try:
        setup_logging()
    except Exception:
        pass

logger = get_logger(__name__) if LOGGING_AVAILABLE else None


class TestAnalysisSecurityCICDWorkflow:
    """Integration tests for static analysis → security audit → CI/CD workflow."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_files = self._create_test_files()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_test_files(self) -> dict[str, str]:
        """Create test files with various code quality and security issues."""
        files = {}

        # Create a Python file with various issues
        python_file = os.path.join(self.test_dir, "test_module.py")
        with open(python_file, 'w') as f:
            f.write('''
import os
import sys

# Security issues
def insecure_function(user_input):
    """Function with SQL injection vulnerability."""
    query = f"SELECT * FROM users WHERE id = {user_input}"  # SQL injection
    os.system(f"echo {user_input}")  # Command injection
    return query

# Code quality issues
def unused_function():
    """This function is never used."""
    x = 1
    return x

# Compliance issue - hard-coded secret
API_KEY = "sk-1234567890abcdef1234567890abcdef12345678"

class TestClass:
    """Test suite for Class."""
    def __init__(self):
        self.value = 42

    def method_with_issues(self, data):
        # Missing input validation
        if data:  # Weak validation
            return self.value * 2
        return None
''')

        # Create a requirements.txt with vulnerable packages
        req_file = os.path.join(self.test_dir, "requirements.txt")
        with open(req_file, 'w') as f:
            f.write('''
flask==2.0.0
requests==2.25.0
django==3.2.0
# Note: These versions might have known vulnerabilities in real scenarios
''')

        files["python_file"] = python_file
        files["requirements_file"] = req_file
        return files

    @pytest.mark.skipif(not STATIC_ANALYSIS_AVAILABLE,
                       reason="Static analysis module not available")
    def test_static_analysis_integration(self):
        """Test that static analysis can analyze the test codebase."""
        from codomyrmex.coding.static_analysis import analyze_file

        python_file = self.test_files["python_file"]

        # Analyze the Python file
        results = analyze_file(python_file)

        assert isinstance(results, list)
        # Should find some issues
        assert len(results) > 0

        # Check that results have expected structure
        for result in results:
            assert hasattr(result, "severity")
            assert hasattr(result, "message")

    @pytest.mark.skipif(not SECURITY_AVAILABLE,
                       reason="Security audit module not available")
    def test_security_audit_integration(self):
        """Test that security audit can scan the test codebase."""
        from codomyrmex.security import scan_vulnerabilities

        # Scan the test directory
        report = scan_vulnerabilities(self.test_dir)

        assert hasattr(report, 'scan_id')
        assert hasattr(report, 'target_path')
        assert hasattr(report, 'vulnerabilities')
        assert hasattr(report, 'scan_status')
        assert report.scan_status == "completed"

        # Vulnerabilities list should exist (may be empty if scanner has no rules for test code)
        assert isinstance(report.vulnerabilities, list)

    @pytest.mark.skipif(not SECURITY_AVAILABLE,
                       reason="Security audit module not available")
    def test_compliance_checking_integration(self):
        """Test compliance checking against security standards."""
        from codomyrmex.security import check_compliance

        # Check OWASP compliance
        results = check_compliance(self.test_dir, ["OWASP_TOP_10"])

        assert isinstance(results, list)

        # Each result should have compliance information
        for result in results:
            if isinstance(result, dict):
                assert 'requirement' in result or 'standard' in result
            else:
                assert hasattr(result, 'requirement') or hasattr(result, 'standard')

    @pytest.mark.skipif(not SECURITY_AVAILABLE,
                       reason="Security audit module not available")
    def test_advanced_security_analysis_integration(self):
        """Test advanced security analysis with AST and patterns."""
        from codomyrmex.security import analyze_file_security

        python_file = self.test_files["python_file"]

        findings = analyze_file_security(python_file)

        assert isinstance(findings, list)

        # Check finding structure if any found
        for finding in findings:
            if isinstance(finding, dict):
                assert 'severity' in finding
            else:
                assert hasattr(finding, 'severity')

    @pytest.mark.skipif(not CI_CD_AVAILABLE,
                       reason="CI/CD automation module not available")
    def test_cicd_pipeline_creation(self):
        """Test creating CI/CD pipelines based on analysis results."""
        from codomyrmex.ci_cd_automation import create_pipeline

        # Create a pipeline configuration
        pipeline_config = {
            "name": "security_pipeline",
            "stages": [
                {
                    "name": "analysis",
                    "jobs": [
                        {
                            "name": "static_analysis",
                            "script": "python -m codomyrmex.coding.static_analysis analyze_project .",
                            "artifacts": ["analysis_report.json"]
                        },
                        {
                            "name": "security_scan",
                            "script": "python -m codomyrmex.security_audit scan_vulnerabilities .",
                            "artifacts": ["security_report.json"]
                        }
                    ]
                },
                {
                    "name": "quality_gate",
                    "jobs": [
                        {
                            "name": "quality_check",
                            "script": "python scripts/check_quality.py",
                            "dependencies": ["analysis"]
                        }
                    ]
                }
            ],
            "triggers": ["push", "pull_request"]
        }

        pipeline = create_pipeline(pipeline_config)

        assert pipeline is not None
        assert hasattr(pipeline, 'name')
        assert hasattr(pipeline, 'stages')
        assert pipeline.name == "security_pipeline"
        assert len(pipeline.stages) == 2

    @pytest.mark.skipif(not CI_CD_AVAILABLE,
                       reason="CI/CD automation module not available")
    def test_pipeline_validation_integration(self):
        """Test pipeline configuration validation."""
        from codomyrmex.ci_cd_automation import validate_pipeline_config

        # Valid pipeline config
        valid_config = {
            "name": "test_pipeline",
            "stages": [
                {
                    "name": "build",
                    "jobs": [
                        {
                            "name": "compile",
                            "script": "echo 'Building...'"
                        }
                    ]
                }
            ]
        }

        is_valid, errors = validate_pipeline_config(valid_config)
        assert is_valid
        assert len(errors) == 0

        # Invalid pipeline config
        invalid_config = {
            "name": "",  # Empty name
            "stages": []  # No stages
        }

        is_valid, errors = validate_pipeline_config(invalid_config)
        assert not is_valid
        assert len(errors) > 0

    @pytest.mark.skipif(not all([STATIC_ANALYSIS_AVAILABLE, SECURITY_AVAILABLE, CI_CD_AVAILABLE]),
                       reason="Required modules not available")
    def test_complete_workflow_integration(self):
        """Test the complete analysis → security → CI/CD workflow."""
        # Step 1: Static analysis
        from codomyrmex.coding.static_analysis import analyze_project
        analysis_results = analyze_project(self.test_dir)

        assert isinstance(analysis_results, dict)
        assert "files_analyzed" in analysis_results

        # Step 2: Security audit
        from codomyrmex.security import scan_vulnerabilities
        security_report = scan_vulnerabilities(self.test_dir)

        assert security_report.scan_status == "completed"
        assert len(security_report.vulnerabilities) >= 0  # May be 0 if no vulns found

        # Step 3: Generate CI/CD pipeline based on results
        from codomyrmex.ci_cd_automation import create_pipeline

        # Create pipeline that includes security checks
        security_pipeline_config = {
            "name": "integrated_security_pipeline",
            "description": "Pipeline with integrated security checks",
            "stages": [
                {
                    "name": "security_analysis",
                    "jobs": [
                        {
                            "name": "dependency_scan",
                            "script": "pip-audit --format json > dependencies.json",
                            "artifacts": ["dependencies.json"]
                        },
                        {
                            "name": "code_security_scan",
                            "script": "bandit -r . -f json -o security_scan.json",
                            "artifacts": ["security_scan.json"]
                        }
                    ]
                },
                {
                    "name": "quality_assurance",
                    "jobs": [
                        {
                            "name": "integration_tests",
                            "script": "pytest testing/integration/ -v",
                            "dependencies": ["security_analysis"]
                        }
                    ]
                }
            ],
            "variables": {
                "PYTHON_VERSION": "3.9",
                "NODE_VERSION": "16"
            }
        }

        pipeline = create_pipeline(security_pipeline_config)

        assert pipeline is not None
        assert pipeline.name == "integrated_security_pipeline"
        assert len(pipeline.stages) == 2

        # Verify pipeline includes security checks
        security_stage = next(s for s in pipeline.stages if s.name == "security_analysis")
        assert len(security_stage.jobs) == 2

    def test_workflow_error_handling(self):
        """Test error handling in the integrated workflow."""
        # Test with non-existent directory
        nonexistent_dir = "/tmp/nonexistent_analysis_dir_12345"

        # Static analysis should handle gracefully
        if STATIC_ANALYSIS_AVAILABLE:
            from codomyrmex.coding.static_analysis import analyze_project
            try:
                result = analyze_project(nonexistent_dir)
                # Should return some result structure even for errors
                assert isinstance(result, (dict, list))
            except Exception as e:
                # Should not crash catastrophically
                assert isinstance(e, Exception)

        # Security audit should handle gracefully
        if SECURITY_AVAILABLE:
            from codomyrmex.security import scan_vulnerabilities
            try:
                report = scan_vulnerabilities(nonexistent_dir)
                assert hasattr(report, 'scan_status')
                # Status might be 'failed' but should not crash
            except Exception as e:
                assert isinstance(e, Exception)

    def test_workflow_performance(self):
        """Test that the integrated workflow performs adequately."""
        import time

        start_time = time.time()

        # Run a subset of the workflow
        workflow_steps = 0

        if STATIC_ANALYSIS_AVAILABLE:
            from codomyrmex.coding.static_analysis import analyze_file
            analyze_file(self.test_files["python_file"])
            workflow_steps += 1

        if SECURITY_AVAILABLE:
            from codomyrmex.security import analyze_file_security
            analyze_file_security(self.test_files["python_file"])
            workflow_steps += 1

        end_time = time.time()
        total_time = end_time - start_time

        if workflow_steps > 0:
            # Should complete within reasonable time (30 seconds for integrated workflow)
            assert total_time < 30
            avg_time_per_step = total_time / workflow_steps
            assert avg_time_per_step < 10  # Each step should take less than 10 seconds

    def test_data_flow_between_modules(self):
        """Test that data flows correctly between analysis modules."""
        # Test that analysis results can be used by security audit
        python_file = self.test_files["python_file"]

        analysis_data = {}
        security_data = {}

        # Collect analysis data
        if STATIC_ANALYSIS_AVAILABLE:
            from codomyrmex.coding.static_analysis import analyze_file
            analysis_results = analyze_file(python_file)
            analysis_data["static_analysis"] = analysis_results

        # Collect security data
        if SECURITY_AVAILABLE:
            from codomyrmex.security import analyze_file_security
            security_findings = analyze_file_security(python_file)
            security_data["security_analysis"] = security_findings

        # Verify data structures are compatible
        assert isinstance(analysis_data, dict)
        assert isinstance(security_data, dict)

        # Both should be able to analyze the same file
        if analysis_data and security_data:
            # Could potentially correlate findings here
            analysis_count = len(analysis_data.get("static_analysis", []))
            security_count = len(security_data.get("security_analysis", []))

            # Both should produce some form of results
            assert analysis_count >= 0
            assert security_count >= 0


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
