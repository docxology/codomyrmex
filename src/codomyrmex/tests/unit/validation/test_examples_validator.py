"""Tests for ExamplesValidator and related dataclasses.

No mocks. Tests real dataclass behavior, enum values,
and ExamplesValidator initialization.
"""


import pytest

from codomyrmex.validation.examples_validator import (
    ExamplesValidator,
    ModuleValidationResult,
    ValidationIssue,
    ValidationSeverity,
    ValidationType,
)


@pytest.mark.unit
class TestValidationSeverity:
    """Tests for ValidationSeverity enum values."""

    def test_critical_value(self):
        """Test functionality: critical value."""
        assert ValidationSeverity.CRITICAL.value == "critical"

    def test_error_value(self):
        """Test functionality: error value."""
        assert ValidationSeverity.ERROR.value == "error"

    def test_warning_value(self):
        """Test functionality: warning value."""
        assert ValidationSeverity.WARNING.value == "warning"

    def test_info_value(self):
        """Test functionality: info value."""
        assert ValidationSeverity.INFO.value == "info"

    def test_member_count(self):
        """Test functionality: member count."""
        assert len(list(ValidationSeverity)) == 4

    def test_is_string_enum(self):
        """Test functionality: is string enum."""
        assert isinstance(ValidationSeverity.CRITICAL, str)
        assert ValidationSeverity.CRITICAL == "critical"


@pytest.mark.unit
class TestValidationType:
    """Tests for ValidationType enum values."""

    def test_execution_value(self):
        """Test functionality: execution value."""
        assert ValidationType.EXECUTION.value == "execution"

    def test_configuration_value(self):
        """Test functionality: configuration value."""
        assert ValidationType.CONFIGURATION.value == "configuration"

    def test_documentation_value(self):
        """Test functionality: documentation value."""
        assert ValidationType.DOCUMENTATION.value == "documentation"

    def test_test_references_value(self):
        """Test functionality: references value."""
        assert ValidationType.TEST_REFERENCES.value == "test_references"

    def test_output_files_value(self):
        """Test functionality: output files value."""
        assert ValidationType.OUTPUT_FILES.value == "output_files"

    def test_member_count(self):
        """Test functionality: member count."""
        assert len(list(ValidationType)) == 5


@pytest.mark.unit
class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_create_with_required_fields(self):
        """Test functionality: create with required fields."""
        issue = ValidationIssue(
            module="test_module",
            validation_type=ValidationType.EXECUTION,
            severity=ValidationSeverity.ERROR,
            message="Test failed",
        )
        assert issue.module == "test_module"
        assert issue.validation_type == ValidationType.EXECUTION
        assert issue.severity == ValidationSeverity.ERROR
        assert issue.message == "Test failed"

    def test_optional_fields_default_to_none(self):
        """Test functionality: optional fields default to none."""
        issue = ValidationIssue(
            module="m",
            validation_type=ValidationType.CONFIGURATION,
            severity=ValidationSeverity.INFO,
            message="msg",
        )
        assert issue.details is None
        assert issue.file_path is None
        assert issue.line_number is None

    def test_create_with_all_fields(self):
        """Test functionality: create with all fields."""
        issue = ValidationIssue(
            module="mymodule",
            validation_type=ValidationType.DOCUMENTATION,
            severity=ValidationSeverity.WARNING,
            message="Missing docstring",
            details="Function foo has no docstring",
            file_path="/src/mymodule/foo.py",
            line_number=42,
        )
        assert issue.line_number == 42
        assert issue.file_path == "/src/mymodule/foo.py"
        assert issue.details == "Function foo has no docstring"


@pytest.mark.unit
class TestModuleValidationResult:
    """Tests for ModuleValidationResult dataclass."""

    def test_successful_result(self):
        """Test functionality: successful result."""
        result = ModuleValidationResult(module="mymodule", success=True)
        assert result.success is True
        assert result.issues == []
        assert result.metadata == {}
        assert result.duration == 0.0

    def test_failed_result_with_issues(self):
        """Test functionality: failed result with issues."""
        issue = ValidationIssue(
            module="mymodule",
            validation_type=ValidationType.EXECUTION,
            severity=ValidationSeverity.CRITICAL,
            message="Import failed",
        )
        result = ModuleValidationResult(
            module="mymodule",
            success=False,
            issues=[issue],
            duration=1.5,
        )
        assert result.success is False
        assert len(result.issues) == 1
        assert result.duration == 1.5

    def test_result_with_metadata(self):
        """Test functionality: result with metadata."""
        result = ModuleValidationResult(
            module="test_mod",
            success=True,
            metadata={"version": "1.0", "tests_run": 5},
        )
        assert result.metadata["version"] == "1.0"
        assert result.metadata["tests_run"] == 5

    def test_multiple_issues(self):
        """Test functionality: multiple issues."""
        issues = [
            ValidationIssue(
                module="mod",
                validation_type=ValidationType.EXECUTION,
                severity=ValidationSeverity.ERROR,
                message=f"Error {i}",
            )
            for i in range(3)
        ]
        result = ModuleValidationResult(module="mod", success=False, issues=issues)
        assert len(result.issues) == 3


@pytest.mark.unit
class TestExamplesValidatorInit:
    """Tests for ExamplesValidator initialization."""

    def test_init_with_required_args(self, tmp_path):
        """Test functionality: init with required args."""
        output_dir = tmp_path / "output"
        validator = ExamplesValidator(
            root_dir=tmp_path,
            output_dir=output_dir,
        )
        assert validator.root_dir == tmp_path
        assert validator.output_dir == output_dir

    def test_default_parallel_jobs(self, tmp_path):
        """Test functionality: default parallel jobs."""
        validator = ExamplesValidator(
            root_dir=tmp_path,
            output_dir=tmp_path / "out",
        )
        assert validator.parallel_jobs == 4

    def test_custom_parallel_jobs(self, tmp_path):
        """Test functionality: custom parallel jobs."""
        validator = ExamplesValidator(
            root_dir=tmp_path,
            output_dir=tmp_path / "out",
            parallel_jobs=2,
        )
        assert validator.parallel_jobs == 2

    def test_init_accepts_path_objects(self, tmp_path):
        """Test functionality: init accepts path objects."""
        root = tmp_path / "root"
        root.mkdir()
        out = tmp_path / "out"
        validator = ExamplesValidator(root_dir=root, output_dir=out)
        assert validator.root_dir == root
        assert validator.output_dir == out
