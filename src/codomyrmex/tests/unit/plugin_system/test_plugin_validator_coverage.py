"""Zero-mock tests for plugin_system.validation.plugin_validator.

Tests PluginValidator methods: validate_plugin_metadata, check_plugin_dependencies,
validate_dockerfile, _scan_file_security, and validate_plugin dispatch.
Uses real temp files for file scanning tests.
"""

import tempfile
from pathlib import Path

from codomyrmex.plugin_system.validation.plugin_validator import (
    PluginValidator,
    ValidationResult,
    validate_plugin,
)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_default_construction(self):
        result = ValidationResult()
        assert result.valid is True
        assert result.issues == []
        assert result.warnings == []
        assert result.security_score == 100.0

    def test_custom_construction(self):
        result = ValidationResult(
            valid=False,
            issues=[{"type": "error", "message": "bad"}],
            warnings=[],
            security_score=60.0,
        )
        assert result.valid is False
        assert len(result.issues) == 1
        assert result.security_score == 60.0


class TestPluginValidatorInit:
    """Tests for PluginValidator initialization."""

    def test_init_sets_risky_imports(self):
        validator = PluginValidator()
        assert "os" in validator.risky_imports
        assert "subprocess" in validator.risky_imports

    def test_init_sets_suspicious_patterns(self):
        validator = PluginValidator()
        assert len(validator.suspicious_patterns) > 0
        # Should have eval pattern
        patterns = [p[0] for p in validator.suspicious_patterns]
        assert any("eval" in p for p in patterns)

    def test_init_sets_risky_dependencies(self):
        validator = PluginValidator()
        assert "cryptography" in validator.risky_dependencies
        assert "paramiko" in validator.risky_dependencies

    def test_init_sets_safe_dependencies(self):
        validator = PluginValidator()
        assert "requests" in validator.safe_dependencies
        assert "pytest" in validator.safe_dependencies


class TestValidatePluginMetadata:
    """Tests for PluginValidator.validate_plugin_metadata method."""

    def test_valid_metadata(self):
        validator = PluginValidator()
        metadata = {"name": "my_plugin", "version": "1.0.0"}
        result = validator.validate_plugin_metadata(metadata)
        assert result.valid is True
        assert result.issues == []

    def test_missing_name_field(self):
        validator = PluginValidator()
        metadata = {"version": "1.0.0"}
        result = validator.validate_plugin_metadata(metadata)
        assert result.valid is False
        messages = [i["message"] for i in result.issues]
        assert any("name" in m for m in messages)

    def test_missing_version_field(self):
        validator = PluginValidator()
        metadata = {"name": "my_plugin"}
        result = validator.validate_plugin_metadata(metadata)
        assert result.valid is False
        messages = [i["message"] for i in result.issues]
        assert any("version" in m for m in messages)

    def test_missing_both_required_fields(self):
        validator = PluginValidator()
        metadata = {"description": "A plugin"}
        result = validator.validate_plugin_metadata(metadata)
        assert result.valid is False
        assert len(result.issues) == 2

    def test_empty_metadata(self):
        validator = PluginValidator()
        result = validator.validate_plugin_metadata({})
        assert result.valid is False
        assert len(result.issues) == 2

    def test_issue_severity_is_error(self):
        validator = PluginValidator()
        result = validator.validate_plugin_metadata({})
        for issue in result.issues:
            assert issue["severity"] == "error"
            assert issue["type"] == "metadata"


class TestCheckPluginDependencies:
    """Tests for PluginValidator.check_plugin_dependencies method."""

    def test_no_dependencies_valid(self):
        validator = PluginValidator()
        result = validator.check_plugin_dependencies([])
        assert result.valid is True
        assert result.issues == []

    def test_safe_dependency_no_warning(self):
        validator = PluginValidator()
        result = validator.check_plugin_dependencies(["requests"])
        assert result.valid is True
        assert result.warnings == []

    def test_risky_dependency_adds_warning(self):
        validator = PluginValidator()
        result = validator.check_plugin_dependencies(["cryptography"])
        assert len(result.warnings) >= 1
        messages = [w["message"] for w in result.warnings]
        assert any("cryptography" in m for m in messages)

    def test_missing_dependency_with_available_list(self):
        validator = PluginValidator()
        result = validator.check_plugin_dependencies(
            ["plugin_a", "plugin_b"], available_plugins=["plugin_a"]
        )
        assert result.valid is False
        messages = [i["message"] for i in result.issues]
        assert any("plugin_b" in m for m in messages)

    def test_all_dependencies_available(self):
        validator = PluginValidator()
        result = validator.check_plugin_dependencies(
            ["plugin_a"], available_plugins=["plugin_a", "plugin_b"]
        )
        assert result.valid is True
        assert result.issues == []

    def test_risky_dep_severity_is_warning(self):
        validator = PluginValidator()
        result = validator.check_plugin_dependencies(["docker"])
        for w in result.warnings:
            assert w["severity"] == "warning"
            assert w["type"] == "dependency"

    def test_missing_dep_severity_is_error(self):
        validator = PluginValidator()
        result = validator.check_plugin_dependencies(
            ["missing_dep"], available_plugins=[]
        )
        for issue in result.issues:
            assert issue["severity"] == "error"
            assert issue["type"] == "dependency"


class TestValidateDockerfile:
    """Tests for PluginValidator.validate_dockerfile method."""

    def test_valid_dockerfile(self):
        validator = PluginValidator()
        content = "FROM python:3.11\nWORKDIR /app\nCOPY . .\nRUN pip install ."
        result = validator.validate_dockerfile(content)
        assert result.valid is True

    def test_missing_from_instruction(self):
        validator = PluginValidator()
        content = "WORKDIR /app\nCOPY . .\nRUN pip install ."
        result = validator.validate_dockerfile(content)
        assert result.valid is False
        messages = [i["message"] for i in result.issues]
        assert any("FROM" in m for m in messages)

    def test_chmod_777_flagged(self):
        validator = PluginValidator()
        content = "FROM ubuntu:latest\nRUN chmod 777 /app"
        result = validator.validate_dockerfile(content)
        assert result.valid is False
        messages = [i["message"] for i in result.issues]
        assert any("permission" in m.lower() or "777" in m for m in messages)

    def test_user_root_adds_warning(self):
        validator = PluginValidator()
        content = "FROM python:3.11\nUSER root\nWORKDIR /app"
        result = validator.validate_dockerfile(content)
        assert len(result.warnings) >= 1
        messages = [w["message"] for w in result.warnings]
        assert any("root" in m.lower() for m in messages)

    def test_secure_dockerfile_no_warnings(self):
        validator = PluginValidator()
        content = "FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nUSER nobody"
        result = validator.validate_dockerfile(content)
        assert result.valid is True
        assert result.warnings == []

    def test_missing_from_issue_type(self):
        validator = PluginValidator()
        result = validator.validate_dockerfile("WORKDIR /app")
        for issue in result.issues:
            if "FROM" in issue.get("message", ""):
                assert issue["type"] == "docker"


class TestScanFileSecurity:
    """Tests for PluginValidator._scan_file_security method."""

    def test_clean_file_scores_100(self):
        validator = PluginValidator()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def add(a, b):\n    return a + b\n")
            fname = f.name
        result = validator._scan_file_security(fname)
        assert result.valid is True
        assert result.security_score == 100.0
        Path(fname).unlink(missing_ok=True)

    def test_file_with_eval_flagged(self):
        validator = PluginValidator()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("user_input = input()\nresult = eval(user_input)\n")
            fname = f.name
        result = validator._scan_file_security(fname)
        assert result.valid is False
        messages = [i["message"] for i in result.issues]
        assert any("eval" in m.lower() for m in messages)
        Path(fname).unlink(missing_ok=True)

    def test_file_with_risky_import_adds_warning(self):
        validator = PluginValidator()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import os\nimport subprocess\n\ndef run():\n    pass\n")
            fname = f.name
        result = validator._scan_file_security(fname)
        assert len(result.warnings) >= 1
        messages = [w["message"] for w in result.warnings]
        assert any("os" in m or "subprocess" in m for m in messages)
        Path(fname).unlink(missing_ok=True)

    def test_file_with_os_system_flagged(self):
        validator = PluginValidator()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import os\n\ndef run(cmd):\n    os.system(cmd)\n")
            fname = f.name
        result = validator._scan_file_security(fname)
        issues = [i["message"] for i in result.issues]
        assert any("shell" in m.lower() or "command" in m.lower() for m in issues)
        Path(fname).unlink(missing_ok=True)

    def test_security_score_decreases_per_issue(self):
        validator = PluginValidator()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import os\nresult = eval('x')\nsubprocess.run(['ls'])\n")
            fname = f.name
        result = validator._scan_file_security(fname)
        assert result.security_score < 100.0
        Path(fname).unlink(missing_ok=True)

    def test_nonexistent_file_returns_invalid(self):
        validator = PluginValidator()
        result = validator._scan_file_security("/nonexistent/path/plugin.py")
        assert result.valid is False
        assert len(result.issues) >= 1


class TestValidatePluginDispatch:
    """Tests for PluginValidator.validate_plugin and validate_plugin function."""

    def test_validate_plugin_with_string_path_to_file(self):
        validator = PluginValidator()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def my_func():\n    return 42\n")
            fname = f.name
        result = validator.validate_plugin(fname)
        assert isinstance(result, ValidationResult)
        Path(fname).unlink(missing_ok=True)

    def test_validate_plugin_with_nonexistent_path(self):
        validator = PluginValidator()
        result = validator.validate_plugin("/no/such/file.py")
        # Not an existing path, not a plugin with .info → returns default ValidationResult
        assert isinstance(result, ValidationResult)

    def test_validate_plugin_with_non_path_non_plugin(self):
        validator = PluginValidator()
        result = validator.validate_plugin(12345)
        assert isinstance(result, ValidationResult)
        assert result.valid is True  # default

    def test_module_level_validate_plugin_function(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# clean file\ndef hello():\n    return 'world'\n")
            fname = f.name
        result = validate_plugin(fname)
        assert isinstance(result, ValidationResult)
        Path(fname).unlink(missing_ok=True)
