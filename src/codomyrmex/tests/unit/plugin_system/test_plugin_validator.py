"""Unit tests for plugin validation -- metadata, security scanning, and dependency checks."""

import os
import tempfile

import pytest

from codomyrmex.plugin_system.core.plugin_registry import (
    Plugin,
    PluginInfo,
    PluginType,
)
from codomyrmex.plugin_system.validation.enforcer import InterfaceEnforcer
from codomyrmex.plugin_system.validation.plugin_validator import (
    PluginValidator,
    validate_plugin,
)


# ============================================================================
# Test Plugin Validator
# ============================================================================

@pytest.mark.unit
class TestPluginValidator:
    """Test cases for PluginValidator functionality."""

    def test_plugin_validator_creation(self):
        """Test creating a plugin validator."""
        validator = PluginValidator()
        assert validator is not None
        assert len(validator.risky_imports) > 0
        assert len(validator.suspicious_patterns) > 0

    def test_validate_plugin_metadata(self):
        """Test plugin metadata validation."""
        validator = PluginValidator()

        # Valid metadata
        valid_metadata = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "author": "Test Author",
            "entry_point": "test_plugin.py"
        }

        result = validator.validate_plugin_metadata(valid_metadata)
        assert result.valid

        # Invalid metadata
        invalid_metadata = {
            "name": "test_plugin",
            # Missing version
            "description": "Test plugin"
            # Missing other required fields
        }

        result = validator.validate_plugin_metadata(invalid_metadata)
        assert not result.valid
        assert len(result.issues) > 0

    def test_validate_metadata_missing_name(self):
        """Test validation fails when name is missing."""
        validator = PluginValidator()

        metadata = {
            "version": "1.0.0",
            "description": "Test"
        }

        result = validator.validate_plugin_metadata(metadata)
        assert not result.valid
        assert any("name" in str(issue).lower() for issue in result.issues)

    def test_security_scanning(self):
        """Test plugin security scanning."""
        validator = PluginValidator()

        # Create test plugin file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import os
import subprocess

def dangerous_function():
    os.system('rm -rf /')  # Very dangerous!
    subprocess.call(['chmod', '777', '/etc/passwd'])
    api_key = 'sk-1234567890abcdef1234567890abcdef'  # Hardcoded secret
""")
            test_file = f.name

        try:
            result = validator.validate_plugin(test_file)

            assert not result.valid
            assert result.security_score < 100

            # Should detect multiple issues
            issue_messages = [issue['message'] for issue in result.issues + result.warnings]
            dangerous_found = any('dangerous' in msg.lower() or 'risky' in msg.lower() for msg in issue_messages)
            assert dangerous_found

        finally:
            os.unlink(test_file)

    def test_security_scanning_safe_plugin(self):
        """Test security scanning on a safe plugin."""
        validator = PluginValidator()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
# Safe plugin with no dangerous patterns
def safe_function(x, y):
    return x + y

class SafePlugin:
    def __init__(self):
        self.data = []

    def process(self, item):
        self.data.append(item)
        return len(self.data)
""")
            test_file = f.name

        try:
            result = validator.validate_plugin(test_file)
            # Should have high security score
            assert result.security_score >= 80
        finally:
            os.unlink(test_file)

    def test_detect_eval_exec(self):
        """Test detection of eval and exec usage."""
        validator = PluginValidator()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def run_code(code_string):
    eval(code_string)
    exec(code_string)
""")
            test_file = f.name

        try:
            result = validator.validate_plugin(test_file)
            assert not result.valid
            issue_messages = [issue['message'].lower() for issue in result.issues]
            assert any('eval' in msg or 'exec' in msg for msg in issue_messages)
        finally:
            os.unlink(test_file)

    def test_dependency_validation(self):
        """Test dependency validation."""
        validator = PluginValidator()

        # Test safe dependencies
        safe_deps = ["requests", "click", "pyyaml"]
        result = validator.check_plugin_dependencies(safe_deps)
        assert result.valid
        assert len(result.issues) == 0

        # Test risky dependencies
        risky_deps = ["cryptography", "paramiko", "docker"]
        result = validator.check_plugin_dependencies(risky_deps)
        assert len(result.warnings) > 0  # Should flag at least some as risky

    def test_dependency_validation_with_available_list(self):
        """Test dependency validation against available plugins."""
        validator = PluginValidator()

        available = ["plugin_a", "plugin_b"]
        required = ["plugin_a", "plugin_c"]

        result = validator.check_plugin_dependencies(required, available)

        assert not result.valid
        assert any("plugin_c" in issue['message'] for issue in result.issues)

    def test_dockerfile_validation(self):
        """Test Dockerfile validation."""
        validator = PluginValidator()

        # Valid Dockerfile
        valid_dockerfile = """FROM ubuntu:20.04
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y python3
USER appuser
CMD ["python", "app.py"]
"""

        result = validator.validate_dockerfile(valid_dockerfile)
        assert result.valid or len(result.issues) == 0  # May have warnings but no errors

        # Invalid Dockerfile
        invalid_dockerfile = """FROM ubuntu:latest
RUN chmod 777 /app
USER root
"""

        result = validator.validate_dockerfile(invalid_dockerfile)
        assert not result.valid or len(result.issues) > 0

    def test_dockerfile_missing_from(self):
        """Test Dockerfile validation without FROM instruction."""
        validator = PluginValidator()

        invalid_dockerfile = """
WORKDIR /app
RUN echo "no from instruction"
"""

        result = validator.validate_dockerfile(invalid_dockerfile)
        assert not result.valid
        assert any("FROM" in issue['message'] for issue in result.issues)

    def test_validate_plugin_instance(self):
        """Test validating a plugin instance."""
        validator = PluginValidator()

        plugin = Plugin(PluginInfo("test", "1.0.0", "", "", PluginType.UTILITY, "test.py"))

        result = validator.validate(plugin)
        assert result.valid

    def test_validate_plugin_missing_methods(self):
        """Test validating plugin without required methods."""
        validator = PluginValidator()

        class IncompletePlugin:
            pass

        result = validator.validate(IncompletePlugin())
        assert not result.valid


# ============================================================================
# Test Interface Enforcer
# ============================================================================

@pytest.mark.unit
class TestInterfaceEnforcer:
    """Test cases for the InterfaceEnforcer."""

    def test_enforcer_valid_interface(self):
        """Test enforcer with valid interface implementation."""
        class RequiredInterface:
            def method_a(self): pass
            def method_b(self): pass

        class ValidImplementation:
            def method_a(self): return "a"
            def method_b(self): return "b"

        result = InterfaceEnforcer.enforce(ValidImplementation(), RequiredInterface)
        assert result is True

    def test_enforcer_invalid_interface(self):
        """Test enforcer with invalid interface implementation."""
        class RequiredInterface:
            def method_a(self): pass
            def method_b(self): pass

        class InvalidImplementation:
            def method_a(self): return "a"
            # Missing method_b

        result = InterfaceEnforcer.enforce(InvalidImplementation(), RequiredInterface)
        assert result is False

    def test_enforcer_partial_implementation(self):
        """Test enforcer with partial interface implementation."""
        class RequiredInterface:
            def method_a(self): pass
            def method_b(self): pass
            def method_c(self): pass

        class PartialImplementation:
            def method_a(self): return "a"
            method_b = "not callable"  # Not a method

        result = InterfaceEnforcer.enforce(PartialImplementation(), RequiredInterface)
        assert result is False
