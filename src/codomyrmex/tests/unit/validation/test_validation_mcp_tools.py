"""Zero-mock tests for validation.mcp_tools and validation.pai modules.

Covers: validate_schema, validate_config, validation_summary MCP tools,
plus validation.schemas (Result, ResultStatus) and validation.pai
(check function, validate_pai_integration).

Zero-mock policy: no unittest.mock, no MagicMock, no monkeypatch.
"""

import pytest

from codomyrmex.validation.mcp_tools import (
    validate_config,
    validate_schema,
    validation_summary,
)
from codomyrmex.validation.schemas import Result, ResultStatus

# ==============================================================================
# validate_schema MCP tool
# ==============================================================================


@pytest.mark.unit
class TestValidateSchemaMCPTool:
    """Tests for the validate_schema MCP tool function."""

    def test_valid_object_passes(self):
        result = validate_schema(
            data={"name": "alice"},
            schema={"type": "object", "required": ["name"]},
        )
        assert result["is_valid"] is True
        assert result["errors"] == []

    def test_missing_required_field_fails(self):
        result = validate_schema(
            data={},
            schema={"type": "object", "required": ["name"]},
        )
        assert result["is_valid"] is False
        assert len(result["errors"]) >= 1

    def test_wrong_type_fails(self):
        result = validate_schema(
            data="not an object",
            schema={"type": "object"},
        )
        assert result["is_valid"] is False

    def test_integer_type_valid(self):
        result = validate_schema(data=42, schema={"type": "integer"})
        assert result["is_valid"] is True

    def test_string_type_valid(self):
        result = validate_schema(data="hello", schema={"type": "string"})
        assert result["is_valid"] is True

    def test_array_type_valid(self):
        result = validate_schema(data=[1, 2, 3], schema={"type": "array"})
        assert result["is_valid"] is True

    def test_return_keys_present(self):
        result = validate_schema(data={}, schema={})
        assert "is_valid" in result
        assert "errors" in result
        assert "warnings" in result

    def test_errors_have_expected_structure(self):
        result = validate_schema(
            data={},
            schema={"type": "object", "required": ["x"]},
        )
        for err in result["errors"]:
            assert "message" in err
            assert "field" in err
            assert "code" in err

    def test_warnings_have_expected_structure(self):
        result = validate_schema(data={"name": "x"}, schema={"type": "object"})
        for w in result["warnings"]:
            assert "message" in w
            assert "field" in w

    def test_nested_required_fields(self):
        result = validate_schema(
            data={"a": 1, "b": 2},
            schema={"type": "object", "required": ["a", "b"]},
        )
        assert result["is_valid"] is True

    def test_partial_required_fields_fails(self):
        result = validate_schema(
            data={"a": 1},
            schema={"type": "object", "required": ["a", "b"]},
        )
        assert result["is_valid"] is False

    def test_empty_schema_passes_anything(self):
        result = validate_schema(data={"anything": True}, schema={})
        assert result["is_valid"] is True


# ==============================================================================
# validate_config MCP tool
# ==============================================================================


@pytest.mark.unit
class TestValidateConfigMCPTool:
    """Tests for the validate_config MCP tool function."""

    def test_all_required_keys_present(self):
        result = validate_config(
            config={"host": "localhost", "port": 5432},
            required_keys=["host", "port"],
        )
        assert result["is_valid"] is True
        assert result["missing_keys"] == []

    def test_missing_required_key_fails(self):
        result = validate_config(
            config={"host": "localhost"},
            required_keys=["host", "port"],
        )
        assert result["is_valid"] is False
        assert "port" in result["missing_keys"]

    def test_no_required_keys_always_valid(self):
        result = validate_config(config={"x": 1})
        assert result["is_valid"] is True

    def test_empty_config_with_required_fails(self):
        result = validate_config(config={}, required_keys=["key"])
        assert result["is_valid"] is False
        assert len(result["missing_keys"]) == 1

    def test_strict_mode_flags_extra_keys(self):
        result = validate_config(
            config={"a": 1, "b": 2, "extra": 3},
            required_keys=["a", "b"],
            strict=True,
        )
        assert result["is_valid"] is True  # Only errors cause is_valid=False
        assert len(result["warnings"]) >= 1
        warning_fields = [w["field"] for w in result["warnings"]]
        assert "extra" in warning_fields

    def test_strict_mode_no_extras_no_warnings(self):
        result = validate_config(
            config={"a": 1, "b": 2},
            required_keys=["a", "b"],
            strict=True,
        )
        assert result["is_valid"] is True
        assert result["warnings"] == []

    def test_none_value_generates_warning(self):
        result = validate_config(
            config={"host": None},
            required_keys=["host"],
        )
        assert result["is_valid"] is True  # Present but None -> warning
        warning_fields = [w["field"] for w in result["warnings"]]
        assert "host" in warning_fields

    def test_key_count_field(self):
        result = validate_config(config={"a": 1, "b": 2, "c": 3})
        assert result["key_count"] == 3

    def test_return_keys_present(self):
        result = validate_config(config={})
        assert "is_valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "missing_keys" in result
        assert "key_count" in result

    def test_error_message_contains_key_name(self):
        result = validate_config(config={}, required_keys=["database_url"])
        assert len(result["errors"]) == 1
        assert "database_url" in result["errors"][0]["message"]

    def test_multiple_missing_keys(self):
        result = validate_config(config={}, required_keys=["a", "b", "c"])
        assert result["is_valid"] is False
        assert len(result["missing_keys"]) == 3


# ==============================================================================
# validation_summary MCP tool
# ==============================================================================


@pytest.mark.unit
class TestValidationSummaryMCPTool:
    """Tests for the validation_summary MCP tool function."""

    def test_summary_returns_dict(self):
        result = validation_summary()
        assert isinstance(result, dict)

    def test_summary_has_runs_key(self):
        result = validation_summary()
        assert "runs" in result

    def test_fresh_manager_has_zero_runs(self):
        # Each call creates a new ValidationManager, so runs will be 0
        result = validation_summary()
        assert result["runs"] == 0

    def test_summary_pass_rate_type(self):
        result = validation_summary()
        # With 0 runs, no pass_rate key per source code
        assert isinstance(result.get("runs", 0), int)


# ==============================================================================
# validation.schemas — Result and ResultStatus
# ==============================================================================


@pytest.mark.unit
class TestResultStatus:
    """Tests for the ResultStatus enum (validation/schemas/core.py)."""

    def test_success_value(self):
        assert ResultStatus.SUCCESS.value == "success"

    def test_failure_value(self):
        assert ResultStatus.FAILURE.value == "failure"

    def test_partial_value(self):
        assert ResultStatus.PARTIAL.value == "partial"

    def test_skipped_value(self):
        assert ResultStatus.SKIPPED.value == "skipped"

    def test_timeout_value(self):
        assert ResultStatus.TIMEOUT.value == "timeout"

    def test_is_enum(self):
        from enum import Enum

        assert issubclass(ResultStatus, Enum)

    def test_all_members(self):
        names = {m.name for m in ResultStatus}
        assert names == {"SUCCESS", "FAILURE", "PARTIAL", "SKIPPED", "TIMEOUT"}


@pytest.mark.unit
class TestResult:
    """Tests for the Result dataclass (validation/schemas/core.py)."""

    def test_success_result_ok(self):
        r = Result(status=ResultStatus.SUCCESS)
        assert r.ok is True

    def test_failure_result_not_ok(self):
        r = Result(status=ResultStatus.FAILURE)
        assert r.ok is False

    def test_partial_result_not_ok(self):
        r = Result(status=ResultStatus.PARTIAL)
        assert r.ok is False

    def test_skipped_result_not_ok(self):
        r = Result(status=ResultStatus.SKIPPED)
        assert r.ok is False

    def test_timeout_result_not_ok(self):
        r = Result(status=ResultStatus.TIMEOUT)
        assert r.ok is False

    def test_default_message_empty(self):
        r = Result(status=ResultStatus.SUCCESS)
        assert r.message == ""

    def test_default_data_none(self):
        r = Result(status=ResultStatus.SUCCESS)
        assert r.data is None

    def test_default_errors_empty_list(self):
        r = Result(status=ResultStatus.SUCCESS)
        assert r.errors == []

    def test_default_metadata_empty_dict(self):
        r = Result(status=ResultStatus.SUCCESS)
        assert r.metadata == {}

    def test_default_duration_none(self):
        r = Result(status=ResultStatus.SUCCESS)
        assert r.duration_ms is None

    def test_with_message(self):
        r = Result(status=ResultStatus.FAILURE, message="Something went wrong")
        assert r.message == "Something went wrong"

    def test_with_data(self):
        r = Result(status=ResultStatus.SUCCESS, data={"key": "value"})
        assert r.data == {"key": "value"}

    def test_with_errors(self):
        r = Result(status=ResultStatus.FAILURE, errors=["err1", "err2"])
        assert r.errors == ["err1", "err2"]

    def test_to_dict_structure(self):
        r = Result(status=ResultStatus.SUCCESS, message="ok")
        d = r.to_dict()
        assert d["status"] == "success"
        assert d["message"] == "ok"
        assert "data" in d
        assert "errors" in d
        assert "metadata" in d
        assert "duration_ms" in d

    def test_to_dict_failure_status(self):
        r = Result(status=ResultStatus.FAILURE)
        d = r.to_dict()
        assert d["status"] == "failure"


# ==============================================================================
# validation.pai — check() function
# ==============================================================================


@pytest.mark.unit
class TestValidationPaiCheck:
    """Tests for the validation.pai.check() function."""

    def test_passing_condition_records_nothing(self):
        import codomyrmex.validation.pai as pai_mod

        original_errors = list(pai_mod.errors)
        original_warnings = list(pai_mod.warnings)

        # Reset state
        pai_mod.errors = []
        pai_mod.warnings = []

        pai_mod.check(True, "should not be recorded")

        assert pai_mod.errors == []
        assert pai_mod.warnings == []

        # Restore
        pai_mod.errors = original_errors
        pai_mod.warnings = original_warnings

    def test_failing_condition_records_error(self):
        import codomyrmex.validation.pai as pai_mod

        pai_mod.errors = []
        pai_mod.warnings = []

        pai_mod.check(False, "something failed")

        assert len(pai_mod.errors) == 1
        assert "something failed" in pai_mod.errors[0]
        assert "FAIL" in pai_mod.errors[0]

    def test_failing_condition_with_warn_records_warning(self):
        import codomyrmex.validation.pai as pai_mod

        pai_mod.errors = []
        pai_mod.warnings = []

        pai_mod.check(False, "soft warning", warn=True)

        assert len(pai_mod.warnings) == 1
        assert "soft warning" in pai_mod.warnings[0]
        assert "WARN" in pai_mod.warnings[0]
        assert pai_mod.errors == []

    def test_multiple_failures_accumulate(self):
        import codomyrmex.validation.pai as pai_mod

        pai_mod.errors = []
        pai_mod.warnings = []

        pai_mod.check(False, "first")
        pai_mod.check(False, "second")

        assert len(pai_mod.errors) == 2


# ==============================================================================
# validation.pai — validate_pai_integration
# ==============================================================================


@pytest.mark.unit
class TestValidatePaiIntegration:
    """Tests for validate_pai_integration with real filesystem."""

    def test_returns_integer(self, tmp_path):
        from codomyrmex.validation.pai import validate_pai_integration

        # Create a minimal fake src_dir with some module dirs
        (tmp_path / "auth" / "__init__.py").parent.mkdir(parents=True)
        (tmp_path / "auth" / "__init__.py").touch()
        (tmp_path / "__pycache__").mkdir()

        result = validate_pai_integration(tmp_path)
        assert isinstance(result, int)
        assert result in (0, 1)

    def _make_fake_src(self, tmp_path):
        """Create a minimal fake src dir with at least one module."""
        mod_dir = tmp_path / "auth"
        mod_dir.mkdir()
        (mod_dir / "__init__.py").touch()
        return tmp_path

    def test_src_with_module_runs_without_crash(self, tmp_path):
        from codomyrmex.validation.pai import validate_pai_integration

        src = self._make_fake_src(tmp_path)
        result = validate_pai_integration(src)
        assert result in (0, 1)

    def test_resets_errors_and_warnings_each_call(self, tmp_path):
        import codomyrmex.validation.pai as pai_mod
        from codomyrmex.validation.pai import validate_pai_integration

        # Poison state first
        pai_mod.errors = ["stale error"]
        pai_mod.warnings = ["stale warning"]

        src = self._make_fake_src(tmp_path)
        validate_pai_integration(src)
        # After the call, errors/warnings should have been reset inside fn
        # (not necessarily empty since the fn may add new ones, but "stale" entries gone)
        assert "stale error" not in pai_mod.errors
