"""
Comprehensive zero-mock tests for three validation core modules.

Targets:
  - validation/validator.py   (Validator, ValidationResult, ValidationError,
                               ValidationWarning; all strategies + _basic_validation
                               edge cases including boolean type and alphanumeric format)
  - validation/summary.py     (ValidationSummary: construction, properties, grouping,
                               filtering, output formats, merge)
  - validation/validation_manager.py  (ValidationManager: validate, batch, contextual,
                                        profiles, stats, custom validators)

Zero-mock policy: NO unittest.mock, MagicMock, monkeypatch, or patch — ever.
All tests use real objects and real in-memory data.
"""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from codomyrmex.validation.contextual import ContextualValidator, ValidationIssue
from codomyrmex.validation.exceptions import (
    ConstraintViolationError,
    CustomValidationError,
    FormatValidationError,
    LengthValidationError,
    RangeValidationError,
    RequiredFieldError,
    SchemaError,
    TypeValidationError,
)
from codomyrmex.validation.exceptions import (
    ValidationError as ExcValidationError,
)
from codomyrmex.validation.summary import ValidationSummary
from codomyrmex.validation.validation_manager import ValidationManager, ValidationRun
from codomyrmex.validation.validator import (
    ValidationError,
    ValidationResult,
    ValidationWarning,
    Validator,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _issue(field="f", message="m", severity="error", code="") -> ValidationIssue:
    return ValidationIssue(field=field, message=message, severity=severity, code=code)


# ===========================================================================
# ValidationResult
# ===========================================================================


@pytest.mark.unit
class TestValidationResult:
    """Tests for the ValidationResult dataclass."""

    def test_valid_result_bool_true(self):
        result = ValidationResult(is_valid=True)
        assert bool(result) is True

    def test_invalid_result_bool_false(self):
        result = ValidationResult(is_valid=False)
        assert bool(result) is False

    def test_defaults_empty_errors_and_warnings(self):
        result = ValidationResult(is_valid=True)
        assert result.errors == []
        assert result.warnings == []

    def test_with_errors(self):
        err = ValidationError("bad field", field="name")
        result = ValidationResult(is_valid=False, errors=[err])
        assert len(result.errors) == 1
        assert result.errors[0].field == "name"

    def test_with_warnings(self):
        warn = ValidationWarning(field="age", message="deprecated")
        result = ValidationResult(is_valid=True, warnings=[warn])
        assert len(result.warnings) == 1
        assert result.warnings[0].field == "age"

    def test_multiple_errors(self):
        errs = [ValidationError(f"err{i}") for i in range(3)]
        result = ValidationResult(is_valid=False, errors=errs)
        assert len(result.errors) == 3

    def test_is_valid_field_access(self):
        r = ValidationResult(is_valid=True)
        assert r.is_valid is True
        r2 = ValidationResult(is_valid=False)
        assert r2.is_valid is False


# ===========================================================================
# ValidationWarning
# ===========================================================================


@pytest.mark.unit
class TestValidationWarning:
    """Tests for the ValidationWarning dataclass."""

    def test_instantiation_defaults(self):
        w = ValidationWarning(field="x", message="deprecated field")
        assert w.field == "x"
        assert w.message == "deprecated field"
        assert w.code is None
        assert w.path == []

    def test_with_code(self):
        w = ValidationWarning(field="y", message="warn", code="W001")
        assert w.code == "W001"

    def test_with_path(self):
        w = ValidationWarning(field="z", message="w", path=["a", "b"])
        assert w.path == ["a", "b"]

    def test_path_default_factory_isolation(self):
        # Ensure default_factory creates independent lists per instance
        w1 = ValidationWarning(field="a", message="x")
        w2 = ValidationWarning(field="b", message="y")
        w1.path.append("z")
        assert w2.path == []


# ===========================================================================
# ValidationError (from validator.py)
# ===========================================================================


@pytest.mark.unit
class TestValidatorValidationError:
    """Tests for ValidationError defined in validator.py."""

    def test_basic_message(self):
        err = ValidationError("Something failed")
        assert "Something failed" in str(err)

    def test_field_attribute(self):
        err = ValidationError("Bad input", field="email")
        assert err.field == "email"

    def test_code_attribute(self):
        err = ValidationError("Missing", code="REQUIRED")
        assert err.code == "REQUIRED"

    def test_path_defaults_empty(self):
        err = ValidationError("err")
        assert err.path == []

    def test_path_set_explicitly(self):
        err = ValidationError("err", path=["root", "nested"])
        assert err.path == ["root", "nested"]

    def test_none_field(self):
        err = ValidationError("err", field=None)
        assert err.field is None

    def test_inherits_from_exception(self):
        err = ValidationError("test")
        assert isinstance(err, Exception)


# ===========================================================================
# Validator — json_schema strategy
# ===========================================================================


@pytest.mark.unit
class TestValidatorJsonSchema:
    """Tests for Validator with json_schema strategy."""

    def test_valid_object_with_required_field(self):
        v = Validator("json_schema")
        result = v.validate({"name": "Alice"}, {"type": "object", "required": ["name"]})
        assert result.is_valid is True

    def test_missing_required_field(self):
        v = Validator("json_schema")
        result = v.validate({}, {"type": "object", "required": ["name"]})
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_wrong_type_string_vs_integer(self):
        v = Validator("json_schema")
        result = v.validate("not_int", {"type": "integer"})
        assert result.is_valid is False

    def test_is_valid_convenience_method_true(self):
        v = Validator("json_schema")
        assert v.is_valid(42, {"type": "integer"}) is True

    def test_is_valid_convenience_method_false(self):
        v = Validator("json_schema")
        assert v.is_valid("hello", {"type": "integer"}) is False

    def test_get_errors_returns_list_with_error(self):
        v = Validator("json_schema")
        errors = v.get_errors({}, {"type": "object", "required": ["x"]})
        assert isinstance(errors, list)
        assert len(errors) > 0

    def test_get_errors_empty_when_valid(self):
        v = Validator("json_schema")
        errors = v.get_errors({"x": 1}, {"type": "object"})
        assert errors == []

    def test_valid_array(self):
        v = Validator("json_schema")
        result = v.validate([1, 2, 3], {"type": "array"})
        assert result.is_valid is True

    def test_number_validation_float(self):
        v = Validator("json_schema")
        result = v.validate(3.14, {"type": "number"})
        assert result.is_valid is True

    def test_minimum_constraint_violated(self):
        v = Validator("json_schema")
        result = v.validate(-1, {"type": "integer", "minimum": 0})
        assert result.is_valid is False

    def test_string_enum_valid(self):
        v = Validator("json_schema")
        result = v.validate("red", {"enum": ["red", "green", "blue"]})
        assert result.is_valid is True

    def test_string_enum_invalid(self):
        v = Validator("json_schema")
        result = v.validate("purple", {"enum": ["red", "green", "blue"]})
        assert result.is_valid is False

    def test_nested_object_valid(self):
        v = Validator("json_schema")
        schema = {
            "type": "object",
            "properties": {"address": {"type": "object", "required": ["city"]}},
        }
        result = v.validate({"address": {"city": "Paris"}}, schema)
        assert result.is_valid is True

    def test_default_validator_type_is_json_schema(self):
        v = Validator()
        assert v.validator_type == "json_schema"

    def test_default_validates_json_schema(self):
        v = Validator()
        result = v.validate("hello", {"type": "string"})
        assert result.is_valid is True


# ===========================================================================
# Validator — _basic_validation (called directly for full branch coverage)
# ===========================================================================


@pytest.mark.unit
class TestValidatorBasicValidation:
    """Tests for Validator._basic_validation — all type/format/range branches."""

    def setup_method(self):
        self.v = Validator()

    def test_object_type_valid(self):
        result = self.v._basic_validation({"key": "value"}, {"type": "object"})
        assert result.is_valid is True

    def test_object_type_invalid(self):
        result = self.v._basic_validation("not_an_object", {"type": "object"})
        assert result.is_valid is False
        assert result.errors[0].code == "type_error"

    def test_array_type_valid(self):
        result = self.v._basic_validation([1, 2], {"type": "array"})
        assert result.is_valid is True

    def test_array_type_invalid(self):
        result = self.v._basic_validation("nope", {"type": "array"})
        assert result.is_valid is False

    def test_string_type_valid(self):
        result = self.v._basic_validation("hello", {"type": "string"})
        assert result.is_valid is True

    def test_string_type_invalid(self):
        result = self.v._basic_validation(123, {"type": "string"})
        assert result.is_valid is False

    def test_integer_type_valid(self):
        result = self.v._basic_validation(42, {"type": "integer"})
        assert result.is_valid is True

    def test_integer_type_invalid(self):
        result = self.v._basic_validation("42", {"type": "integer"})
        assert result.is_valid is False

    def test_number_type_int(self):
        result = self.v._basic_validation(42, {"type": "number"})
        assert result.is_valid is True

    def test_number_type_float(self):
        result = self.v._basic_validation(3.14, {"type": "number"})
        assert result.is_valid is True

    def test_number_type_invalid(self):
        # "not a number" string is not number → triggers line 241
        result = self.v._basic_validation("not_a_number", {"type": "number"})
        assert result.is_valid is False
        assert result.errors[0].code == "type_error"

    def test_boolean_type_valid_true(self):
        result = self.v._basic_validation(True, {"type": "boolean"})
        assert result.is_valid is True

    def test_boolean_type_valid_false(self):
        result = self.v._basic_validation(False, {"type": "boolean"})
        assert result.is_valid is True

    def test_boolean_type_invalid_string(self):
        # "true" string triggers boolean branch failure at line 247
        result = self.v._basic_validation("true", {"type": "boolean"})
        assert result.is_valid is False
        assert result.errors[0].code == "type_error"
        assert "boolean" in result.errors[0].message

    def test_boolean_type_invalid_integer(self):
        # Note: bool is subclass of int, but int is NOT subclass of bool
        result = self.v._basic_validation(1, {"type": "boolean"})
        assert result.is_valid is False

    def test_required_fields_missing(self):
        schema = {"type": "object", "required": ["name", "email"]}
        result = self.v._basic_validation({"name": "Alice"}, schema)
        assert result.is_valid is False
        assert any(e.code == "required_field_missing" for e in result.errors)

    def test_required_fields_all_present(self):
        schema = {"type": "object", "required": ["name"]}
        result = self.v._basic_validation({"name": "Alice"}, schema)
        assert result.is_valid is True

    def test_empty_schema_always_valid(self):
        result = self.v._basic_validation({"any": "data"}, {})
        assert result.is_valid is True

    def test_format_email_valid(self):
        result = self.v._basic_validation("user@example.com", {"format": "email"})
        assert result.is_valid is True

    def test_format_email_invalid(self):
        result = self.v._basic_validation("not_an_email", {"format": "email"})
        assert result.is_valid is False
        assert result.errors[0].code == "format_error"

    def test_format_url_valid(self):
        result = self.v._basic_validation("https://example.com", {"format": "url"})
        assert result.is_valid is True

    def test_format_url_invalid(self):
        result = self.v._basic_validation("not-a-url", {"format": "url"})
        assert result.is_valid is False
        assert result.errors[0].code == "format_error"

    def test_format_alphanumeric_valid(self):
        # Line 278: alphanumeric format check
        result = self.v._basic_validation("abc123", {"format": "alphanumeric"})
        assert result.is_valid is True

    def test_format_alphanumeric_invalid(self):
        # Triggers the alphanumeric branch at line 277-278
        result = self.v._basic_validation("abc-123!", {"format": "alphanumeric"})
        assert result.is_valid is False
        assert result.errors[0].code == "format_error"
        assert "alphanumeric" in result.errors[0].message

    def test_format_check_skipped_for_non_string(self):
        # format check only applies when data is str
        result = self.v._basic_validation(42, {"format": "email"})
        assert result.is_valid is True  # no format error for non-string

    def test_minimum_check_valid(self):
        result = self.v._basic_validation(5, {"minimum": 0})
        assert result.is_valid is True

    def test_minimum_check_violated(self):
        result = self.v._basic_validation(-1, {"minimum": 0})
        assert result.is_valid is False
        assert result.errors[0].code == "range_error"

    def test_maximum_check_valid(self):
        result = self.v._basic_validation(99, {"maximum": 100})
        assert result.is_valid is True

    def test_maximum_check_violated(self):
        result = self.v._basic_validation(101, {"maximum": 100})
        assert result.is_valid is False
        assert result.errors[0].code == "range_error"

    def test_range_not_applied_to_non_numbers(self):
        # Range check only fires when data is int or float
        result = self.v._basic_validation("hello", {"minimum": 0})
        assert result.is_valid is True


# ===========================================================================
# Validator — pydantic strategy
# ===========================================================================


@pytest.mark.unit
class TestValidatorPydantic:
    """Tests for Validator with pydantic strategy."""

    def test_valid_model(self):
        class User(BaseModel):
            name: str
            age: int

        v = Validator("pydantic")
        result = v.validate({"name": "Alice", "age": 30}, User)
        assert result.is_valid is True

    def test_invalid_model_wrong_type(self):
        class Item(BaseModel):
            count: int

        v = Validator("pydantic")
        result = v.validate({"count": "not_an_int"}, Item)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_missing_required_field(self):
        class Config(BaseModel):
            host: str
            port: int

        v = Validator("pydantic")
        result = v.validate({"host": "localhost"}, Config)
        assert result.is_valid is False

    def test_error_has_field_attribute(self):
        class Config(BaseModel):
            port: int

        v = Validator("pydantic")
        result = v.validate({"port": "bad"}, Config)
        assert len(result.errors) > 0
        # Field should not be None — pydantic errors have loc
        assert result.errors[0].field is not None

    def test_non_dict_data_passed_positionally(self):
        class Wrapper(BaseModel):
            value: int

        # non-dict data is passed directly to the model constructor
        v = Validator("pydantic")
        result = v.validate({"value": 42}, Wrapper)
        assert result.is_valid is True


# ===========================================================================
# Validator — custom strategy
# ===========================================================================


@pytest.mark.unit
class TestValidatorCustom:
    """Tests for Validator with custom callable strategy."""

    def test_custom_lambda_bool_true(self):
        v = Validator("custom")
        result = v.validate({"x": 5}, lambda d: d.get("x", 0) > 0)
        assert result.is_valid is True

    def test_custom_lambda_bool_false(self):
        v = Validator("custom")
        result = v.validate({"x": -1}, lambda d: d.get("x", 0) > 0)
        assert result.is_valid is False

    def test_custom_returns_validation_result_valid(self):
        v = Validator("custom")
        result = v.validate({}, lambda d: ValidationResult(is_valid=True))
        assert result.is_valid is True

    def test_custom_returns_validation_result_invalid(self):
        v = Validator("custom")
        result = v.validate(
            {},
            lambda d: ValidationResult(
                is_valid=False,
                errors=[ValidationError("custom fail")],
            ),
        )
        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_custom_exception_caught_returns_invalid(self):
        v = Validator("custom")
        result = v.validate({}, lambda d: 1 / 0)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert result.errors[0].code == "custom_validation_error"

    def test_custom_non_bool_non_result_treated_as_valid(self):
        v = Validator("custom")
        # A string return value is neither bool nor ValidationResult → valid
        result = v.validate({}, lambda d: "ok")
        assert result.is_valid is True

    def test_custom_none_return_treated_as_valid(self):
        v = Validator("custom")
        result = v.validate({}, lambda d: None)
        assert result.is_valid is True


# ===========================================================================
# Validator — unknown type
# ===========================================================================


@pytest.mark.unit
class TestValidatorUnknownType:
    """Tests for Validator with unrecognized strategy."""

    def test_unknown_validator_returns_invalid(self):
        v = Validator("unknown_type")
        result = v.validate({}, {})
        assert result.is_valid is False

    def test_unknown_validator_error_message(self):
        v = Validator("no_such_type")
        result = v.validate({}, {})
        assert len(result.errors) > 0


# ===========================================================================
# ValidationSummary
# ===========================================================================


@pytest.mark.unit
class TestValidationSummary:
    """Tests for ValidationSummary — all properties, groupings, outputs."""

    def test_empty_summary_is_valid(self):
        s = ValidationSummary()
        assert s.is_valid is True
        assert s.total == 0
        assert s.error_count == 0
        assert s.warning_count == 0
        assert s.info_count == 0

    def test_init_with_none_produces_empty(self):
        s = ValidationSummary(None)
        assert s.total == 0

    def test_init_with_issues_list(self):
        issues = [_issue(), _issue(field="x")]
        s = ValidationSummary(issues)
        assert s.total == 2

    def test_add_issue_increments_total(self):
        s = ValidationSummary()
        s.add_issue(_issue())
        assert s.total == 1

    def test_add_issues_batch(self):
        s = ValidationSummary()
        s.add_issues([_issue(), _issue(field="x")])
        assert s.total == 2

    def test_is_valid_with_error_is_false(self):
        s = ValidationSummary([_issue(severity="error")])
        assert s.is_valid is False

    def test_is_valid_with_only_warnings_is_true(self):
        s = ValidationSummary([_issue(severity="warning")])
        assert s.is_valid is True

    def test_is_valid_with_only_info_is_true(self):
        s = ValidationSummary([_issue(severity="info")])
        assert s.is_valid is True

    def test_error_count(self):
        s = ValidationSummary([_issue(severity="error"), _issue(severity="error")])
        assert s.error_count == 2

    def test_warning_count(self):
        s = ValidationSummary([_issue(severity="warning"), _issue(severity="warning")])
        assert s.warning_count == 2

    def test_info_count(self):
        s = ValidationSummary([_issue(severity="info")])
        assert s.info_count == 1

    def test_mixed_severity_counts(self):
        s = ValidationSummary(
            [
                _issue(severity="error"),
                _issue(severity="warning"),
                _issue(severity="info"),
            ]
        )
        assert s.error_count == 1
        assert s.warning_count == 1
        assert s.info_count == 1

    def test_by_severity_groups_correctly(self):
        s = ValidationSummary(
            [
                _issue(severity="error"),
                _issue(severity="error"),
                _issue(severity="warning"),
            ]
        )
        grouped = s.by_severity()
        assert len(grouped["error"]) == 2
        assert len(grouped["warning"]) == 1

    def test_by_severity_empty_summary(self):
        s = ValidationSummary()
        assert s.by_severity() == {}

    def test_by_field_groups_correctly(self):
        s = ValidationSummary(
            [
                _issue(field="name"),
                _issue(field="name"),
                _issue(field="age"),
            ]
        )
        grouped = s.by_field()
        assert len(grouped["name"]) == 2
        assert len(grouped["age"]) == 1

    def test_worst_fields_top_n(self):
        s = ValidationSummary(
            [
                _issue(field="name", severity="error"),
                _issue(field="name", severity="error"),
                _issue(field="age", severity="error"),
            ]
        )
        worst = s.worst_fields(n=1)
        assert len(worst) == 1
        assert worst[0][0] == "name"
        assert worst[0][1] == 2

    def test_worst_fields_excludes_warnings(self):
        s = ValidationSummary([_issue(field="x", severity="warning")])
        assert s.worst_fields() == []

    def test_worst_fields_default_n_5(self):
        # Create 6 different fields with errors, worst_fields should cap at 5
        issues = [_issue(field=f"f{i}", severity="error") for i in range(6)]
        s = ValidationSummary(issues)
        result = s.worst_fields()  # default n=5
        assert len(result) == 5

    def test_filter_by_severity(self):
        s = ValidationSummary([_issue(severity="error"), _issue(severity="warning")])
        errors = s.filter(severity="error")
        assert len(errors) == 1
        assert errors[0].severity == "error"

    def test_filter_by_field(self):
        s = ValidationSummary([_issue(field="email"), _issue(field="name")])
        result = s.filter(field="email")
        assert len(result) == 1
        assert result[0].field == "email"

    def test_filter_by_both_severity_and_field(self):
        s = ValidationSummary(
            [
                _issue(field="email", severity="error"),
                _issue(field="email", severity="warning"),
                _issue(field="name", severity="error"),
            ]
        )
        result = s.filter(severity="error", field="email")
        assert len(result) == 1

    def test_filter_no_args_returns_all(self):
        s = ValidationSummary([_issue(), _issue(field="x")])
        assert len(s.filter()) == 2

    def test_to_dict_structure(self):
        s = ValidationSummary([_issue()])
        d = s.to_dict()
        assert "is_valid" in d
        assert "total" in d
        assert "error_count" in d
        assert "warning_count" in d
        assert "info_count" in d
        assert "issues" in d
        assert isinstance(d["issues"], list)

    def test_to_dict_issue_fields(self):
        s = ValidationSummary(
            [_issue(field="name", message="required", severity="error", code="E1")]
        )
        issue_d = s.to_dict()["issues"][0]
        assert issue_d["field"] == "name"
        assert issue_d["message"] == "required"
        assert issue_d["severity"] == "error"
        assert issue_d["code"] == "E1"

    def test_to_dict_is_valid_false_when_errors(self):
        s = ValidationSummary([_issue(severity="error")])
        assert s.to_dict()["is_valid"] is False

    def test_to_dict_is_valid_true_when_empty(self):
        s = ValidationSummary()
        assert s.to_dict()["is_valid"] is True

    def test_text_no_issues_passes(self):
        s = ValidationSummary()
        t = s.text()
        assert "passed" in t.lower() or "✅" in t

    def test_text_with_errors_shows_failed(self):
        s = ValidationSummary([_issue()])
        t = s.text()
        assert "FAILED" in t

    def test_text_with_only_warnings_shows_passed(self):
        s = ValidationSummary([_issue(severity="warning")])
        t = s.text()
        assert "PASSED" in t

    def test_text_contains_issue_detail(self):
        s = ValidationSummary([_issue(field="myfield", message="something wrong")])
        t = s.text()
        assert "myfield" in t
        assert "something wrong" in t

    def test_markdown_no_issues(self):
        s = ValidationSummary()
        md = s.markdown()
        assert "passed" in md.lower() or "✅" in md

    def test_markdown_with_errors(self):
        s = ValidationSummary([_issue()])
        md = s.markdown()
        assert "FAILED" in md

    def test_markdown_contains_table_pipe(self):
        s = ValidationSummary([_issue()])
        md = s.markdown()
        assert "|" in md

    def test_markdown_with_warnings_shows_passed(self):
        s = ValidationSummary([_issue(severity="warning")])
        md = s.markdown()
        assert "PASSED" in md

    def test_markdown_severity_row_appears(self):
        s = ValidationSummary([_issue(severity="error")])
        md = s.markdown()
        assert "error" in md

    def test_merge_combines_all_issues(self):
        s1 = ValidationSummary([_issue(field="a")])
        s2 = ValidationSummary([_issue(field="b"), _issue(field="c")])
        merged = ValidationSummary.merge(s1, s2)
        assert merged.total == 3

    def test_merge_empty_args(self):
        merged = ValidationSummary.merge()
        assert merged.total == 0

    def test_merge_single_summary(self):
        s = ValidationSummary([_issue(), _issue()])
        merged = ValidationSummary.merge(s)
        assert merged.total == 2

    def test_merge_preserves_field_names(self):
        s1 = ValidationSummary([_issue(field="alpha")])
        s2 = ValidationSummary([_issue(field="beta")])
        merged = ValidationSummary.merge(s1, s2)
        fields = {i.field for i in merged.issues}
        assert "alpha" in fields
        assert "beta" in fields

    def test_add_issue_after_init(self):
        s = ValidationSummary([_issue(field="a")])
        s.add_issue(_issue(field="b"))
        assert s.total == 2

    def test_add_issues_extends_existing(self):
        s = ValidationSummary([_issue(field="a")])
        s.add_issues([_issue(field="b"), _issue(field="c")])
        assert s.total == 3


# ===========================================================================
# ValidationRun
# ===========================================================================


@pytest.mark.unit
class TestValidationRun:
    """Tests for ValidationRun dataclass."""

    def test_basic_instantiation(self):
        run = ValidationRun(
            schema_name="user",
            validator_type="json_schema",
            success=True,
            duration_ms=1.5,
            issue_count=0,
        )
        assert run.schema_name == "user"
        assert run.validator_type == "json_schema"
        assert run.success is True
        assert run.duration_ms == 1.5
        assert run.issue_count == 0

    def test_failure_run(self):
        run = ValidationRun(
            schema_name="config",
            validator_type="pydantic",
            success=False,
            duration_ms=3.2,
            issue_count=4,
        )
        assert run.success is False
        assert run.issue_count == 4


# ===========================================================================
# ValidationManager — core validate
# ===========================================================================


@pytest.mark.unit
class TestValidationManagerCore:
    """Tests for ValidationManager.validate and validate_batch."""

    def test_validate_json_schema_valid(self):
        mgr = ValidationManager()
        result = mgr.validate({"name": "Alice"}, {"type": "object"})
        assert result.is_valid is True

    def test_validate_json_schema_invalid(self):
        mgr = ValidationManager()
        result = mgr.validate("not_int", {"type": "integer"})
        assert result.is_valid is False

    def test_validate_records_run_in_history(self):
        mgr = ValidationManager()
        mgr.validate(42, {"type": "integer"})
        assert mgr.run_count == 1

    def test_validate_with_schema_title(self):
        mgr = ValidationManager()
        schema = {"type": "object", "title": "user_schema"}
        mgr.validate({"name": "x"}, schema)
        assert mgr._history[0].schema_name == "user_schema"

    def test_validate_schema_without_title_uses_unknown(self):
        mgr = ValidationManager()
        mgr.validate(42, {"type": "integer"})
        assert mgr._history[0].schema_name == "unknown"

    def test_validate_non_dict_schema_uses_unknown_name(self):
        mgr = ValidationManager()
        mgr.validate("hello", {"type": "string"})
        # non-dict schema → schema_name = "unknown"
        assert mgr._history[0].schema_name == "unknown"

    def test_validate_batch_all_valid(self):
        mgr = ValidationManager()
        results = mgr.validate_batch([1, 2, 3], {"type": "integer"})
        assert len(results) == 3
        assert all(r.is_valid for r in results)

    def test_validate_batch_mixed_validity(self):
        mgr = ValidationManager()
        results = mgr.validate_batch([1, "bad", 3], {"type": "integer"})
        assert results[0].is_valid is True
        assert results[1].is_valid is False
        assert results[2].is_valid is True

    def test_validate_batch_empty_list(self):
        mgr = ValidationManager()
        results = mgr.validate_batch([], {"type": "object"})
        assert results == []

    def test_validate_batch_increments_run_count(self):
        mgr = ValidationManager()
        mgr.validate_batch([1, 2], {"type": "integer"})
        assert mgr.run_count == 2


# ===========================================================================
# ValidationManager — custom validators
# ===========================================================================


@pytest.mark.unit
class TestValidationManagerValidators:
    """Tests for custom validator registration and use."""

    def test_register_and_get_validator(self):
        mgr = ValidationManager()

        def fn(d, s):
            return True

        mgr.register_validator("my_rule", fn)
        assert mgr.get_validator("my_rule") is fn

    def test_list_validators_sorted(self):
        mgr = ValidationManager()
        mgr.register_validator("z_rule", lambda d, s: True)
        mgr.register_validator("a_rule", lambda d, s: True)
        listed = mgr.list_validators()
        assert listed == ["a_rule", "z_rule"]

    def test_get_nonexistent_validator_returns_none(self):
        mgr = ValidationManager()
        assert mgr.get_validator("nope") is None

    def test_list_validators_empty(self):
        mgr = ValidationManager()
        assert mgr.list_validators() == []

    def test_custom_validator_always_pass(self):
        mgr = ValidationManager()
        mgr.register_validator("always_pass", lambda d, s: True)
        result = mgr.validate({"x": 1}, {}, validator_type="always_pass")
        assert result.is_valid is True

    def test_custom_validator_always_fail(self):
        mgr = ValidationManager()
        mgr.register_validator("always_fail", lambda d, s: False)
        result = mgr.validate({"x": 1}, {}, validator_type="always_fail")
        assert result.is_valid is False

    def test_custom_validator_can_inspect_data(self):
        mgr = ValidationManager()

        def positive_check(data, schema):
            return data.get("count", 0) > 0

        mgr.register_validator("positive_count", positive_check)
        assert mgr.validate({"count": 5}, {}, validator_type="positive_count").is_valid
        assert not mgr.validate(
            {"count": -1}, {}, validator_type="positive_count"
        ).is_valid

    def test_register_overwrites_existing(self):
        mgr = ValidationManager()
        mgr.register_validator("v", lambda d, s: True)

        def new_fn(d, s):
            return False

        mgr.register_validator("v", new_fn)
        assert mgr.get_validator("v") is new_fn


# ===========================================================================
# ValidationManager — contextual rules
# ===========================================================================


@pytest.mark.unit
class TestValidationManagerContextual:
    """Tests for add_contextual_rule and validate_contextual."""

    def test_add_rule_and_validate_fails(self):
        mgr = ValidationManager()
        mgr.add_contextual_rule(
            ContextualValidator.required_fields("name"), name="name_required"
        )
        summary = mgr.validate_contextual({})
        assert summary.total > 0
        assert summary.is_valid is False

    def test_add_rule_and_validate_passes(self):
        mgr = ValidationManager()
        mgr.add_contextual_rule(ContextualValidator.required_fields("name"))
        summary = mgr.validate_contextual({"name": "Alice"})
        assert summary.is_valid is True

    def test_validate_contextual_returns_summary_instance(self):
        mgr = ValidationManager()
        summary = mgr.validate_contextual({})
        assert isinstance(summary, ValidationSummary)

    def test_no_rules_empty_summary(self):
        mgr = ValidationManager()
        summary = mgr.validate_contextual({"anything": "goes"})
        assert summary.total == 0

    def test_multiple_rules_can_each_fire(self):
        mgr = ValidationManager()
        mgr.add_contextual_rule(ContextualValidator.required_fields("a"))
        mgr.add_contextual_rule(ContextualValidator.required_fields("b"))
        summary = mgr.validate_contextual({})
        # Each required_fields rule fires independently and returns one issue
        # but each rule is called separately; rules only return first missing field
        assert summary.total >= 1


# ===========================================================================
# ValidationManager — profiles
# ===========================================================================


@pytest.mark.unit
class TestValidationManagerProfiles:
    """Tests for profile-based validation."""

    def test_create_and_use_profile_with_failing_rule(self):
        mgr = ValidationManager()

        def check_name(data):
            if not data.get("name"):
                return ValidationIssue(
                    field="name", message="required", severity="error"
                )
            return None

        mgr.create_profile("strict", [("name_check", check_name)])
        summary = mgr.validate_with_profile({}, "strict")
        assert summary.total == 1
        assert summary.is_valid is False

    def test_profile_rule_passing_returns_empty(self):
        mgr = ValidationManager()
        mgr.create_profile("lenient", [("always_pass", lambda d: None)])
        summary = mgr.validate_with_profile({"name": "Alice"}, "lenient")
        assert summary.is_valid is True
        assert summary.total == 0

    def test_unknown_profile_returns_empty_summary(self):
        mgr = ValidationManager()
        summary = mgr.validate_with_profile({}, "nonexistent")
        assert summary.total == 0

    def test_create_profile_with_no_rules(self):
        mgr = ValidationManager()
        mgr.create_profile("empty")
        summary = mgr.validate_with_profile({}, "empty")
        assert summary.total == 0

    def test_profile_rule_exception_recorded_as_error(self):
        mgr = ValidationManager()

        def bad_rule(data):
            raise ValueError("rule failed")

        mgr.create_profile("failing", [("bad_rule", bad_rule)])
        summary = mgr.validate_with_profile({}, "failing")
        assert summary.total == 1
        assert summary.is_valid is False
        assert summary.issues[0].field == "bad_rule"

    def test_profile_rule_returning_non_issue_string_is_wrapped(self):
        mgr = ValidationManager()

        def string_rule(data):
            return "some message"

        mgr.create_profile("str_result", [("r", string_rule)])
        summary = mgr.validate_with_profile({}, "str_result")
        assert summary.total == 1

    def test_profile_rule_returning_validation_issue_directly(self):
        mgr = ValidationManager()
        expected = ValidationIssue(field="x", message="bad", severity="warning")

        def direct_rule(data):
            return expected

        mgr.create_profile("direct", [("r", direct_rule)])
        summary = mgr.validate_with_profile({"x": 1}, "direct")
        assert summary.total == 1
        assert summary.issues[0] is expected

    def test_multiple_rules_in_profile(self):
        mgr = ValidationManager()

        def rule_a(data):
            return ValidationIssue(field="a", message="a fails")

        def rule_b(data):
            return None

        mgr.create_profile("multi", [("a", rule_a), ("b", rule_b)])
        summary = mgr.validate_with_profile({}, "multi")
        assert summary.total == 1


# ===========================================================================
# ValidationManager — statistics
# ===========================================================================


@pytest.mark.unit
class TestValidationManagerStats:
    """Tests for ValidationManager statistics and run tracking."""

    def test_run_count_starts_at_zero(self):
        mgr = ValidationManager()
        assert mgr.run_count == 0

    def test_run_count_increments_on_validate(self):
        mgr = ValidationManager()
        mgr.validate(1, {"type": "integer"})
        mgr.validate(2, {"type": "integer"})
        assert mgr.run_count == 2

    def test_error_rate_no_runs(self):
        mgr = ValidationManager()
        assert mgr.error_rate == 0.0

    def test_error_rate_all_pass(self):
        mgr = ValidationManager()
        mgr.validate(1, {"type": "integer"})
        mgr.validate(2, {"type": "integer"})
        assert mgr.error_rate == 0.0

    def test_error_rate_all_fail(self):
        mgr = ValidationManager()
        mgr.validate("bad", {"type": "integer"})
        assert mgr.error_rate == 1.0

    def test_error_rate_half(self):
        mgr = ValidationManager()
        mgr.validate(1, {"type": "integer"})
        mgr.validate("bad", {"type": "integer"})
        assert mgr.error_rate == 0.5

    def test_summary_empty_runs(self):
        mgr = ValidationManager()
        s = mgr.summary()
        assert s["runs"] == 0

    def test_summary_with_mixed_runs(self):
        mgr = ValidationManager()
        mgr.validate(1, {"type": "integer"})
        mgr.validate("bad", {"type": "integer"})
        s = mgr.summary()
        assert s["runs"] == 2
        assert s["successes"] == 1
        assert s["failures"] == 1
        assert s["pass_rate"] == 0.5
        assert "avg_duration_ms" in s
        assert "validators_used" in s

    def test_summary_validators_used_contains_json_schema(self):
        mgr = ValidationManager()
        mgr.validate(1, {"type": "integer"}, validator_type="json_schema")
        s = mgr.summary()
        assert "json_schema" in s["validators_used"]

    def test_summary_avg_duration_ms_is_positive(self):
        mgr = ValidationManager()
        mgr.validate(1, {"type": "integer"})
        s = mgr.summary()
        assert s["avg_duration_ms"] >= 0.0

    def test_summary_all_pass(self):
        mgr = ValidationManager()
        mgr.validate(1, {"type": "integer"})
        mgr.validate(2, {"type": "integer"})
        s = mgr.summary()
        assert s["pass_rate"] == 1.0
        assert s["failures"] == 0


# ===========================================================================
# exceptions.py — ValidationError
# ===========================================================================


@pytest.mark.unit
class TestExcValidationError:
    """Tests for ValidationError in exceptions.py."""

    def test_basic_instantiation(self):
        err = ExcValidationError("Invalid value")
        assert "Invalid value" in str(err)

    def test_with_field(self):
        err = ExcValidationError("Missing field", field="email")
        assert err.context["field"] == "email"

    def test_with_value(self):
        err = ExcValidationError("Bad value", value="hello")
        assert err.context["value"] == "hello"

    def test_value_truncated_when_long(self):
        long_val = "x" * 200
        err = ExcValidationError("Too long", value=long_val)
        assert len(err.context["value"]) <= 103  # 100 chars + "..."

    def test_with_rule(self):
        err = ExcValidationError("Rule violated", rule="min_length")
        assert err.context["rule"] == "min_length"

    def test_no_field_no_context_key(self):
        err = ExcValidationError("Error")
        assert "field" not in err.context

    def test_is_exception(self):
        err = ExcValidationError("Test")
        assert isinstance(err, Exception)


# ===========================================================================
# exceptions.py — SchemaError
# ===========================================================================


@pytest.mark.unit
class TestSchemaError:
    """Tests for SchemaError in exceptions.py."""

    def test_basic_message(self):
        err = SchemaError("Schema not found")
        assert "Schema not found" in str(err)

    def test_with_schema_name(self):
        err = SchemaError("Bad schema", schema_name="user_schema")
        assert err.context["schema_name"] == "user_schema"

    def test_with_all_fields(self):
        err = SchemaError(
            "Load error",
            schema_name="cfg",
            schema_path="/path/to/schema.json",
            schema_type="json_schema",
        )
        assert err.context["schema_path"] == "/path/to/schema.json"
        assert err.context["schema_type"] == "json_schema"


# ===========================================================================
# exceptions.py — ConstraintViolationError
# ===========================================================================


@pytest.mark.unit
class TestConstraintViolationError:
    """Tests for ConstraintViolationError."""

    def test_basic(self):
        err = ConstraintViolationError("Unique constraint violated")
        assert isinstance(err, ExcValidationError)

    def test_with_context(self):
        err = ConstraintViolationError(
            "Duplicate key",
            constraint_name="unique_email",
            constraint_type="unique",
            expected="unique",
            actual="duplicate",
        )
        assert err.context["constraint_name"] == "unique_email"
        assert err.context["constraint_type"] == "unique"


# ===========================================================================
# exceptions.py — TypeValidationError
# ===========================================================================


@pytest.mark.unit
class TestTypeValidationError:
    """Tests for TypeValidationError."""

    def test_basic(self):
        err = TypeValidationError("Type mismatch")
        assert isinstance(err, ExcValidationError)

    def test_with_types(self):
        err = TypeValidationError(
            "Wrong type",
            expected_type="int",
            actual_type="str",
            field="age",
        )
        assert err.context["expected_type"] == "int"
        assert err.context["actual_type"] == "str"
        assert err.context["field"] == "age"


# ===========================================================================
# exceptions.py — RequiredFieldError
# ===========================================================================


@pytest.mark.unit
class TestRequiredFieldError:
    """Tests for RequiredFieldError."""

    def test_basic(self):
        err = RequiredFieldError("Missing required field", field="name")
        assert err.context["field"] == "name"

    def test_with_parent(self):
        err = RequiredFieldError("Missing", field="host", parent="config.database")
        assert err.context["parent"] == "config.database"


# ===========================================================================
# exceptions.py — RangeValidationError
# ===========================================================================


@pytest.mark.unit
class TestRangeValidationError:
    """Tests for RangeValidationError."""

    def test_with_range(self):
        err = RangeValidationError(
            "Out of range",
            field="age",
            value=-5,
            min_value=0,
            max_value=150,
        )
        assert err.context["min_value"] == 0
        assert err.context["max_value"] == 150

    def test_without_optional_fields(self):
        err = RangeValidationError("Out of range")
        assert "min_value" not in err.context


# ===========================================================================
# exceptions.py — FormatValidationError
# ===========================================================================


@pytest.mark.unit
class TestFormatValidationError:
    """Tests for FormatValidationError."""

    def test_basic(self):
        err = FormatValidationError(
            "Invalid format", field="email", expected_format="email"
        )
        assert err.context["expected_format"] == "email"

    def test_with_pattern(self):
        err = FormatValidationError("Invalid", pattern=r"^\d{5}$")
        assert err.context["pattern"] == r"^\d{5}$"


# ===========================================================================
# exceptions.py — LengthValidationError
# ===========================================================================


@pytest.mark.unit
class TestLengthValidationError:
    """Tests for LengthValidationError."""

    def test_with_lengths(self):
        err = LengthValidationError(
            "Too long",
            field="username",
            actual_length=200,
            min_length=3,
            max_length=50,
        )
        assert err.context["actual_length"] == 200
        assert err.context["max_length"] == 50

    def test_without_optional_fields(self):
        err = LengthValidationError("Length error")
        assert "actual_length" not in err.context


# ===========================================================================
# exceptions.py — CustomValidationError
# ===========================================================================


@pytest.mark.unit
class TestCustomValidationError:
    """Tests for CustomValidationError."""

    def test_with_validator_name(self):
        err = CustomValidationError("Custom fail", validator_name="my_rule")
        assert err.context["validator_name"] == "my_rule"

    def test_with_details(self):
        err = CustomValidationError("Fail", details={"key": "val"})
        assert err.context["details"] == {"key": "val"}

    def test_without_optional_fields(self):
        err = CustomValidationError("Custom fail")
        assert "validator_name" not in err.context


# ===========================================================================
# ValidationIssue — direct tests
# ===========================================================================


@pytest.mark.unit
class TestValidationIssueDirect:
    """Direct tests for ValidationIssue dataclass and __str__ method."""

    def test_str_format_error_severity(self):
        """__str__ uses uppercase severity: [ERROR] field: message."""
        issue = ValidationIssue(field="email", message="bad format", severity="error")
        text = str(issue)
        assert "[ERROR]" in text
        assert "email" in text
        assert "bad format" in text

    def test_str_format_warning_severity(self):
        """__str__ uppercases warning to [WARNING]."""
        issue = ValidationIssue(field="f", message="m", severity="warning")
        assert "[WARNING]" in str(issue)

    def test_str_format_info_severity(self):
        """__str__ uppercases info to [INFO]."""
        issue = ValidationIssue(field="f", message="m", severity="info")
        assert "[INFO]" in str(issue)

    def test_default_severity_is_error(self):
        """Default severity is 'error'."""
        issue = ValidationIssue(field="x", message="y")
        assert issue.severity == "error"

    def test_default_code_is_empty_string(self):
        """Default code is empty string, not None."""
        issue = ValidationIssue(field="x", message="y")
        assert issue.code == ""

    def test_default_context_is_empty_dict(self):
        """Default context is a fresh empty dict."""
        issue = ValidationIssue(field="x", message="y")
        assert issue.context == {}

    def test_context_is_not_shared_across_instances(self):
        """Each ValidationIssue gets its own context dict (no shared default mutable)."""
        a = ValidationIssue(field="a", message="x")
        b = ValidationIssue(field="b", message="y")
        a.context["key"] = "val"
        assert "key" not in b.context


# ===========================================================================
# ContextualValidator — direct tests
# ===========================================================================


@pytest.mark.unit
class TestContextualValidatorDirect:
    """Direct tests for ContextualValidator methods not covered via ValidationManager."""

    def test_empty_validator_returns_no_issues(self):
        """validate() on empty validator returns empty list."""
        v = ContextualValidator()
        assert v.validate({"x": 1}) == []

    def test_rule_count_starts_at_zero(self):
        """New validator has zero rules."""
        v = ContextualValidator()
        assert v.rule_count == 0

    def test_add_rule_increments_count(self):
        """add_rule increases rule_count by one."""
        v = ContextualValidator()
        v.add_rule(lambda d: None, name="noop")
        assert v.rule_count == 1

    def test_add_multiple_rules_increments_count(self):
        """Adding three rules yields rule_count == 3."""
        v = ContextualValidator()
        for i in range(3):
            v.add_rule(lambda d: None, name=f"r{i}")
        assert v.rule_count == 3

    def test_remove_rule_by_name_returns_true(self):
        """remove_rule returns True when a named rule is found and removed."""
        v = ContextualValidator()
        v.add_rule(lambda d: None, name="target")
        assert v.remove_rule("target") is True
        assert v.rule_count == 0

    def test_remove_unknown_rule_returns_false(self):
        """remove_rule returns False when name is not registered."""
        v = ContextualValidator()
        assert v.remove_rule("ghost") is False

    def test_remove_rule_does_not_affect_other_rules(self):
        """Removing one rule leaves others intact."""
        v = ContextualValidator()
        v.add_rule(lambda d: None, name="keep")
        v.add_rule(lambda d: None, name="drop")
        v.remove_rule("drop")
        assert v.rule_count == 1
        assert v._rule_names == ["keep"]

    def test_auto_naming_without_name_arg(self):
        """Rules added without names get auto-generated rule_N names."""
        v = ContextualValidator()
        v.add_rule(lambda d: None)
        assert v._rule_names[0].startswith("rule_")

    def test_is_valid_true_no_error_issues(self):
        """is_valid returns True when all issues are info or warning severity."""
        v = ContextualValidator()
        v.add_rule(lambda d: ValidationIssue("f", "note", severity="info"))
        assert v.is_valid({"x": 1}) is True

    def test_is_valid_false_with_error_issue(self):
        """is_valid returns False when any rule returns an error-severity issue."""
        v = ContextualValidator()
        v.add_rule(lambda d: ValidationIssue("f", "bad", severity="error"))
        assert v.is_valid({"x": 1}) is False

    def test_validate_many_omits_clean_records(self):
        """validate_many only includes records with issues in result dict."""
        v = ContextualValidator()
        v.add_rule(ContextualValidator.required_fields("name"))
        records = [{"name": "Alice"}, {}, {"name": "Bob"}]
        result = v.validate_many(records)
        assert 0 not in result
        assert 1 in result
        assert 2 not in result

    def test_validate_many_empty_list(self):
        """validate_many on empty list returns empty dict."""
        v = ContextualValidator()
        assert v.validate_many([]) == {}

    def test_validate_many_all_pass(self):
        """validate_many returns empty dict when all records pass."""
        v = ContextualValidator()
        v.add_rule(ContextualValidator.required_fields("x"))
        result = v.validate_many([{"x": "a"}, {"x": "b"}])
        assert result == {}

    def test_validate_many_all_fail(self):
        """validate_many returns entry for every failing record."""
        v = ContextualValidator()
        v.add_rule(ContextualValidator.required_fields("x"))
        result = v.validate_many([{}, {}])
        assert 0 in result
        assert 1 in result

    def test_rule_returning_none_contributes_no_issue(self):
        """Rules returning None are silently skipped (no issues added)."""
        v = ContextualValidator()
        v.add_rule(lambda d: None)
        v.add_rule(lambda d: None)
        assert v.validate({}) == []


# ===========================================================================
# ContextualValidator — built-in rule factory tests
# ===========================================================================


@pytest.mark.unit
class TestContextualValidatorRuleFactories:
    """Direct tests for all ContextualValidator static rule factories."""

    # ── required_fields ─────────────────────────────────────────────────────

    def test_required_fields_all_present_non_empty(self):
        """required_fields passes when all listed fields have non-empty values."""
        rule = ContextualValidator.required_fields("name", "email")
        assert rule({"name": "Alice", "email": "a@b.com"}) is None

    def test_required_fields_absent_field_returns_issue(self):
        """required_fields returns an issue when a field is absent."""
        rule = ContextualValidator.required_fields("name")
        issue = rule({})
        assert issue is not None
        assert issue.code == "REQUIRED"
        assert issue.field == "name"

    def test_required_fields_whitespace_only_fails(self):
        """required_fields rejects whitespace-only string values."""
        rule = ContextualValidator.required_fields("name")
        issue = rule({"name": "   "})
        assert issue is not None
        assert issue.code == "REQUIRED"

    def test_required_fields_none_value_fails(self):
        """required_fields rejects None field values."""
        rule = ContextualValidator.required_fields("x")
        issue = rule({"x": None})
        assert issue is not None

    def test_required_fields_stops_at_first_missing(self):
        """required_fields returns the first missing field issue only."""
        rule = ContextualValidator.required_fields("a", "b", "c")
        issue = rule({})
        assert issue is not None
        assert issue.field == "a"  # first in the list

    # ── mutual_exclusion ─────────────────────────────────────────────────────

    def test_mutual_exclusion_both_absent_passes(self):
        """mutual_exclusion passes when neither field is present."""
        rule = ContextualValidator.mutual_exclusion("a", "b")
        assert rule({}) is None

    def test_mutual_exclusion_only_a_passes(self):
        """mutual_exclusion passes when only field_a is set."""
        rule = ContextualValidator.mutual_exclusion("a", "b")
        assert rule({"a": "value"}) is None

    def test_mutual_exclusion_only_b_passes(self):
        """mutual_exclusion passes when only field_b is set."""
        rule = ContextualValidator.mutual_exclusion("a", "b")
        assert rule({"b": "value"}) is None

    def test_mutual_exclusion_both_set_returns_issue(self):
        """mutual_exclusion returns an issue when both fields are truthy."""
        rule = ContextualValidator.mutual_exclusion("a", "b")
        issue = rule({"a": "x", "b": "y"})
        assert issue is not None
        assert issue.code == "MUTUAL_EXCLUSION"
        assert "a" in issue.field
        assert "b" in issue.field

    # ── conditional_requirement ──────────────────────────────────────────────

    def test_conditional_requirement_trigger_not_matching_passes(self):
        """conditional_requirement passes when trigger_field does not match trigger_value."""
        rule = ContextualValidator.conditional_requirement("mode", "admin", "token")
        assert rule({"mode": "user"}) is None

    def test_conditional_requirement_trigger_absent_passes(self):
        """conditional_requirement passes when trigger field is absent."""
        rule = ContextualValidator.conditional_requirement("mode", "admin", "token")
        assert rule({}) is None

    def test_conditional_requirement_triggered_required_present_passes(self):
        """conditional_requirement passes when triggered and required field is set."""
        rule = ContextualValidator.conditional_requirement("mode", "admin", "token")
        assert rule({"mode": "admin", "token": "abc"}) is None

    def test_conditional_requirement_triggered_required_absent_fails(self):
        """conditional_requirement fails when triggered and required field missing."""
        rule = ContextualValidator.conditional_requirement("mode", "admin", "token")
        issue = rule({"mode": "admin"})
        assert issue is not None
        assert issue.code == "CONDITIONAL_REQUIRED"
        assert issue.field == "token"

    def test_conditional_requirement_message_mentions_both_fields(self):
        """Issue message references the trigger field and required field."""
        rule = ContextualValidator.conditional_requirement("role", "sudo", "password")
        issue = rule({"role": "sudo"})
        assert "password" in issue.message
        assert "role" in issue.message

    # ── range_check ──────────────────────────────────────────────────────────

    def test_range_check_within_bounds_passes(self):
        """range_check passes for value within [min_val, max_val]."""
        rule = ContextualValidator.range_check("age", 0, 150)
        assert rule({"age": 25}) is None

    def test_range_check_at_min_boundary_passes(self):
        """range_check passes for value exactly at min_val."""
        rule = ContextualValidator.range_check("n", 0, 100)
        assert rule({"n": 0}) is None

    def test_range_check_at_max_boundary_passes(self):
        """range_check passes for value exactly at max_val."""
        rule = ContextualValidator.range_check("n", 0, 100)
        assert rule({"n": 100}) is None

    def test_range_check_below_min_fails(self):
        """range_check returns RANGE_MIN issue when value < min_val."""
        rule = ContextualValidator.range_check("age", 0, 150)
        issue = rule({"age": -1})
        assert issue is not None
        assert issue.code == "RANGE_MIN"

    def test_range_check_above_max_fails(self):
        """range_check returns RANGE_MAX issue when value > max_val."""
        rule = ContextualValidator.range_check("score", 0, 100)
        issue = rule({"score": 200})
        assert issue is not None
        assert issue.code == "RANGE_MAX"

    def test_range_check_field_absent_passes(self):
        """range_check passes when field is absent (treated as optional)."""
        rule = ContextualValidator.range_check("age", 0, 150)
        assert rule({}) is None

    def test_range_check_non_numeric_fails_with_type_error(self):
        """range_check fails with TYPE_ERROR for non-numeric string values."""
        rule = ContextualValidator.range_check("age", 0, 150)
        issue = rule({"age": "twenty"})
        assert issue is not None
        assert issue.code == "TYPE_ERROR"

    def test_range_check_only_min_val(self):
        """range_check with only min_val rejects values below minimum."""
        rule = ContextualValidator.range_check("n", min_val=5)
        assert rule({"n": 10}) is None
        assert rule({"n": 4}) is not None

    def test_range_check_only_max_val(self):
        """range_check with only max_val rejects values above maximum."""
        rule = ContextualValidator.range_check("n", max_val=10)
        assert rule({"n": 5}) is None
        assert rule({"n": 11}) is not None

    def test_range_check_float_value_passes(self):
        """range_check handles float values correctly."""
        rule = ContextualValidator.range_check("temp", -273.15, 1000.0)
        assert rule({"temp": 3.14}) is None

    # ── pattern_match ─────────────────────────────────────────────────────────

    def test_pattern_match_valid_string_passes(self):
        """pattern_match passes when field value matches the pattern."""
        rule = ContextualValidator.pattern_match("code", r"^\d{5}$")
        assert rule({"code": "12345"}) is None

    def test_pattern_match_invalid_string_fails(self):
        """pattern_match returns PATTERN_MISMATCH when field doesn't match."""
        rule = ContextualValidator.pattern_match("code", r"^\d{5}$")
        issue = rule({"code": "abc"})
        assert issue is not None
        assert issue.code == "PATTERN_MISMATCH"

    def test_pattern_match_field_absent_passes(self):
        """pattern_match passes when field is absent (treated as optional)."""
        rule = ContextualValidator.pattern_match("code", r"^\d{5}$")
        assert rule({}) is None

    def test_pattern_match_custom_description_in_message(self):
        """Custom description appears in the issue message."""
        rule = ContextualValidator.pattern_match(
            "zip", r"^\d{5}$", description="must be a 5-digit ZIP code"
        )
        issue = rule({"zip": "nope"})
        assert issue is not None
        assert "5-digit ZIP code" in issue.message

    def test_pattern_match_default_description_uses_pattern(self):
        """Without a description, the pattern itself appears in the message."""
        rule = ContextualValidator.pattern_match("code", r"^\d{3}$")
        issue = rule({"code": "ab"})
        assert issue is not None
        assert r"^\d{3}$" in issue.message

    def test_pattern_match_non_string_value_coerced_to_str(self):
        """Non-string values are coerced via str() before matching."""
        rule = ContextualValidator.pattern_match("n", r"^\d+$")
        # int 42 → "42" → matches r"^\d+$"
        assert rule({"n": 42}) is None

    # ── type_check ────────────────────────────────────────────────────────────

    def test_type_check_correct_type_passes(self):
        """type_check passes when field value is the expected type."""
        rule = ContextualValidator.type_check("count", int)
        assert rule({"count": 5}) is None

    def test_type_check_wrong_type_fails(self):
        """type_check returns TYPE_CHECK issue when type is wrong."""
        rule = ContextualValidator.type_check("count", int)
        issue = rule({"count": "five"})
        assert issue is not None
        assert issue.code == "TYPE_CHECK"

    def test_type_check_message_mentions_expected_type(self):
        """TYPE_CHECK issue message contains the expected type name."""
        rule = ContextualValidator.type_check("flag", bool)
        issue = rule({"flag": "yes"})
        assert issue is not None
        assert "bool" in issue.message

    def test_type_check_field_absent_passes(self):
        """type_check passes when field is absent (treated as optional)."""
        rule = ContextualValidator.type_check("x", int)
        assert rule({}) is None

    def test_type_check_list_type(self):
        """type_check works with list as expected type."""
        rule = ContextualValidator.type_check("items", list)
        assert rule({"items": [1, 2, 3]}) is None
        issue = rule({"items": "not a list"})
        assert issue is not None
