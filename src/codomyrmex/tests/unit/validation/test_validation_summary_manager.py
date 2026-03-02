"""
Unit tests for validation.summary and validation.validation_manager — Zero-Mock compliant.

Covers:
  - validation/contextual.py  (ValidationIssue, ContextualValidator + built-in rules)
  - validation/summary.py     (ValidationSummary: add, properties, grouping, output)
  - validation/validation_manager.py  (ValidationManager: validate, batch, contextual,
                                        profiles, stats)
"""

import pytest

from codomyrmex.validation.contextual import ContextualValidator, ValidationIssue
from codomyrmex.validation.summary import ValidationSummary
from codomyrmex.validation.validation_manager import ValidationManager, ValidationRun

# ── ValidationIssue ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_basic_instantiation(self):
        issue = ValidationIssue(field="name", message="required")
        assert issue.field == "name"
        assert issue.message == "required"
        assert issue.severity == "error"
        assert issue.code == ""
        assert issue.context == {}

    def test_custom_severity(self):
        issue = ValidationIssue(field="age", message="deprecated", severity="warning")
        assert issue.severity == "warning"

    def test_with_code(self):
        issue = ValidationIssue(field="x", message="m", code="E001")
        assert issue.code == "E001"

    def test_str_format(self):
        issue = ValidationIssue(field="email", message="invalid format", severity="error")
        s = str(issue)
        assert "ERROR" in s
        assert "email" in s
        assert "invalid format" in s

    def test_with_context(self):
        issue = ValidationIssue(field="f", message="m", context={"key": "val"})
        assert issue.context["key"] == "val"


# ── ContextualValidator ────────────────────────────────────────────────────


@pytest.mark.unit
class TestContextualValidator:
    """Tests for ContextualValidator."""

    def test_empty_validate_returns_empty(self):
        v = ContextualValidator()
        assert v.validate({}) == []

    def test_add_rule_increments_count(self):
        v = ContextualValidator()
        v.add_rule(lambda d: None)
        assert v.rule_count == 1

    def test_rule_returning_none_no_issues(self):
        v = ContextualValidator()
        v.add_rule(lambda d: None)
        assert v.validate({"x": 1}) == []

    def test_rule_returning_issue(self):
        v = ContextualValidator()
        issue = ValidationIssue(field="x", message="bad")
        v.add_rule(lambda d: issue)
        result = v.validate({})
        assert len(result) == 1
        assert result[0] is issue

    def test_remove_rule_by_name(self):
        v = ContextualValidator()
        v.add_rule(lambda d: None, name="my_rule")
        assert v.rule_count == 1
        removed = v.remove_rule("my_rule")
        assert removed is True
        assert v.rule_count == 0

    def test_remove_nonexistent_returns_false(self):
        v = ContextualValidator()
        assert v.remove_rule("nope") is False

    def test_is_valid_no_errors(self):
        v = ContextualValidator()
        v.add_rule(lambda d: ValidationIssue(field="f", message="m", severity="warning"))
        assert v.is_valid({}) is True

    def test_is_valid_with_error(self):
        v = ContextualValidator()
        v.add_rule(lambda d: ValidationIssue(field="f", message="m", severity="error"))
        assert v.is_valid({}) is False

    def test_validate_many_returns_dict(self):
        v = ContextualValidator()
        v.add_rule(ContextualValidator.required_fields("name"))
        result = v.validate_many([{"name": "Alice"}, {}, {"name": "Bob"}])
        assert 0 not in result  # Alice is valid
        assert 1 in result      # empty dict fails
        assert 2 not in result  # Bob is valid

    def test_required_fields_missing(self):
        rule = ContextualValidator.required_fields("email")
        issue = rule({})
        assert issue is not None
        assert issue.field == "email"
        assert issue.code == "REQUIRED"

    def test_required_fields_empty_string(self):
        rule = ContextualValidator.required_fields("name")
        issue = rule({"name": "   "})
        assert issue is not None

    def test_required_fields_present(self):
        rule = ContextualValidator.required_fields("name")
        issue = rule({"name": "Alice"})
        assert issue is None

    def test_mutual_exclusion_both_set(self):
        rule = ContextualValidator.mutual_exclusion("a", "b")
        issue = rule({"a": "x", "b": "y"})
        assert issue is not None
        assert issue.code == "MUTUAL_EXCLUSION"

    def test_mutual_exclusion_only_one(self):
        rule = ContextualValidator.mutual_exclusion("a", "b")
        assert rule({"a": "x"}) is None
        assert rule({"b": "y"}) is None

    def test_conditional_requirement_triggered(self):
        rule = ContextualValidator.conditional_requirement("type", "admin", "token")
        issue = rule({"type": "admin"})
        assert issue is not None
        assert issue.field == "token"
        assert issue.code == "CONDITIONAL_REQUIRED"

    def test_conditional_requirement_not_triggered(self):
        rule = ContextualValidator.conditional_requirement("type", "admin", "token")
        assert rule({"type": "user"}) is None

    def test_conditional_requirement_satisfied(self):
        rule = ContextualValidator.conditional_requirement("type", "admin", "token")
        assert rule({"type": "admin", "token": "abc"}) is None

    def test_range_check_below_min(self):
        rule = ContextualValidator.range_check("age", min_val=0)
        issue = rule({"age": -1})
        assert issue is not None
        assert issue.code == "RANGE_MIN"

    def test_range_check_above_max(self):
        rule = ContextualValidator.range_check("age", max_val=150)
        issue = rule({"age": 200})
        assert issue is not None
        assert issue.code == "RANGE_MAX"

    def test_range_check_in_range(self):
        rule = ContextualValidator.range_check("age", min_val=0, max_val=150)
        assert rule({"age": 25}) is None

    def test_range_check_missing_field_no_issue(self):
        rule = ContextualValidator.range_check("score", min_val=0)
        assert rule({}) is None

    def test_range_check_non_numeric(self):
        rule = ContextualValidator.range_check("score", min_val=0)
        issue = rule({"score": "not_a_number"})
        assert issue is not None
        assert issue.code == "TYPE_ERROR"

    def test_pattern_match_passes(self):
        rule = ContextualValidator.pattern_match("zip", r"^\d{5}$")
        assert rule({"zip": "12345"}) is None

    def test_pattern_match_fails(self):
        rule = ContextualValidator.pattern_match("zip", r"^\d{5}$")
        issue = rule({"zip": "abc"})
        assert issue is not None
        assert issue.code == "PATTERN_MISMATCH"

    def test_pattern_match_missing_field_no_issue(self):
        rule = ContextualValidator.pattern_match("zip", r"^\d{5}$")
        assert rule({}) is None

    def test_type_check_passes(self):
        rule = ContextualValidator.type_check("count", int)
        assert rule({"count": 5}) is None

    def test_type_check_fails(self):
        rule = ContextualValidator.type_check("count", int)
        issue = rule({"count": "five"})
        assert issue is not None
        assert issue.code == "TYPE_CHECK"

    def test_type_check_missing_field_no_issue(self):
        rule = ContextualValidator.type_check("count", int)
        assert rule({}) is None


# ── ValidationSummary ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestValidationSummary:
    """Tests for ValidationSummary."""

    def _issue(self, field="f", message="m", severity="error", code=""):
        return ValidationIssue(field=field, message=message, severity=severity, code=code)

    def test_empty_summary_is_valid(self):
        s = ValidationSummary()
        assert s.is_valid is True
        assert s.total == 0

    def test_add_issue_increments_total(self):
        s = ValidationSummary()
        s.add_issue(self._issue())
        assert s.total == 1

    def test_add_issues_batch(self):
        s = ValidationSummary()
        s.add_issues([self._issue(), self._issue(field="x")])
        assert s.total == 2

    def test_is_valid_with_error_is_false(self):
        s = ValidationSummary([self._issue(severity="error")])
        assert s.is_valid is False

    def test_is_valid_with_only_warnings(self):
        s = ValidationSummary([self._issue(severity="warning")])
        assert s.is_valid is True

    def test_error_count(self):
        s = ValidationSummary([
            self._issue(severity="error"),
            self._issue(severity="warning"),
            self._issue(severity="info"),
        ])
        assert s.error_count == 1
        assert s.warning_count == 1
        assert s.info_count == 1

    def test_by_severity_groups_correctly(self):
        s = ValidationSummary([
            self._issue(severity="error"),
            self._issue(severity="error"),
            self._issue(severity="warning"),
        ])
        grouped = s.by_severity()
        assert len(grouped["error"]) == 2
        assert len(grouped["warning"]) == 1

    def test_by_field_groups_correctly(self):
        s = ValidationSummary([
            self._issue(field="name"),
            self._issue(field="name"),
            self._issue(field="age"),
        ])
        grouped = s.by_field()
        assert len(grouped["name"]) == 2
        assert len(grouped["age"]) == 1

    def test_worst_fields_returns_top_n(self):
        s = ValidationSummary([
            self._issue(field="name", severity="error"),
            self._issue(field="name", severity="error"),
            self._issue(field="age", severity="error"),
        ])
        worst = s.worst_fields(n=1)
        assert len(worst) == 1
        assert worst[0][0] == "name"
        assert worst[0][1] == 2

    def test_worst_fields_only_errors(self):
        s = ValidationSummary([
            self._issue(field="x", severity="warning"),
        ])
        # warnings don't count
        assert s.worst_fields() == []

    def test_filter_by_severity(self):
        s = ValidationSummary([
            self._issue(severity="error"),
            self._issue(severity="warning"),
        ])
        errors = s.filter(severity="error")
        assert len(errors) == 1
        assert errors[0].severity == "error"

    def test_filter_by_field(self):
        s = ValidationSummary([
            self._issue(field="email"),
            self._issue(field="name"),
        ])
        result = s.filter(field="email")
        assert len(result) == 1
        assert result[0].field == "email"

    def test_filter_by_both(self):
        s = ValidationSummary([
            self._issue(field="email", severity="error"),
            self._issue(field="email", severity="warning"),
            self._issue(field="name", severity="error"),
        ])
        result = s.filter(severity="error", field="email")
        assert len(result) == 1

    def test_to_dict_structure(self):
        s = ValidationSummary([self._issue()])
        d = s.to_dict()
        assert "is_valid" in d
        assert "total" in d
        assert "error_count" in d
        assert "issues" in d
        assert isinstance(d["issues"], list)

    def test_to_dict_issue_has_fields(self):
        s = ValidationSummary([self._issue(field="name", message="required", severity="error", code="E1")])
        d = s.to_dict()
        issue_d = d["issues"][0]
        assert issue_d["field"] == "name"
        assert issue_d["message"] == "required"
        assert issue_d["severity"] == "error"
        assert issue_d["code"] == "E1"

    def test_text_no_issues(self):
        s = ValidationSummary()
        t = s.text()
        assert "passed" in t.lower() or "✅" in t

    def test_text_with_errors(self):
        s = ValidationSummary([self._issue()])
        t = s.text()
        assert "FAILED" in t

    def test_text_with_only_warnings(self):
        s = ValidationSummary([self._issue(severity="warning")])
        t = s.text()
        assert "PASSED" in t or "passed" in t.lower()

    def test_markdown_no_issues(self):
        s = ValidationSummary()
        md = s.markdown()
        assert "passed" in md.lower() or "✅" in md

    def test_markdown_with_errors(self):
        s = ValidationSummary([self._issue()])
        md = s.markdown()
        assert "FAILED" in md

    def test_markdown_contains_table(self):
        s = ValidationSummary([self._issue()])
        md = s.markdown()
        assert "|" in md  # markdown table

    def test_merge_combines_issues(self):
        s1 = ValidationSummary([self._issue(field="a")])
        s2 = ValidationSummary([self._issue(field="b"), self._issue(field="c")])
        merged = ValidationSummary.merge(s1, s2)
        assert merged.total == 3

    def test_merge_empty(self):
        merged = ValidationSummary.merge()
        assert merged.total == 0

    def test_init_with_issues_list(self):
        issues = [self._issue(), self._issue(field="x")]
        s = ValidationSummary(issues)
        assert s.total == 2


# ── ValidationRun ──────────────────────────────────────────────────────────


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
        assert run.success is True
        assert run.duration_ms == 1.5
        assert run.issue_count == 0


# ── ValidationManager ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestValidationManagerCore:
    """Tests for ValidationManager core validation."""

    def test_validate_json_schema_valid(self):
        mgr = ValidationManager()
        result = mgr.validate({"name": "Alice"}, {"type": "object"})
        assert result.is_valid is True

    def test_validate_json_schema_invalid(self):
        mgr = ValidationManager()
        result = mgr.validate("not_int", {"type": "integer"})
        assert result.is_valid is False

    def test_validate_records_run(self):
        mgr = ValidationManager()
        mgr.validate(42, {"type": "integer"})
        assert mgr.run_count == 1

    def test_validate_batch_all_valid(self):
        mgr = ValidationManager()
        schema = {"type": "integer"}
        results = mgr.validate_batch([1, 2, 3], schema)
        assert len(results) == 3
        assert all(r.is_valid for r in results)

    def test_validate_batch_mixed(self):
        mgr = ValidationManager()
        schema = {"type": "integer"}
        results = mgr.validate_batch([1, "bad", 3], schema)
        assert results[0].is_valid is True
        assert results[1].is_valid is False
        assert results[2].is_valid is True

    def test_validate_batch_empty(self):
        mgr = ValidationManager()
        results = mgr.validate_batch([], {"type": "object"})
        assert results == []

    def test_validate_with_title_schema(self):
        mgr = ValidationManager()
        schema = {"type": "object", "title": "user_schema"}
        mgr.validate({"name": "x"}, schema)
        # Should record schema_name from title
        assert mgr._history[0].schema_name == "user_schema"


@pytest.mark.unit
class TestValidationManagerValidators:
    """Tests for validator registration."""

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

    def test_get_nonexistent_returns_none(self):
        mgr = ValidationManager()
        assert mgr.get_validator("nope") is None

    def test_custom_validator_used(self):
        mgr = ValidationManager()

        def always_pass(data, schema):
            return True

        mgr.register_validator("always_pass", always_pass)
        result = mgr.validate({"x": 1}, {}, validator_type="always_pass")
        assert result.is_valid is True

    def test_custom_validator_fail(self):
        mgr = ValidationManager()

        def always_fail(data, schema):
            return False

        mgr.register_validator("always_fail", always_fail)
        result = mgr.validate({"x": 1}, {}, validator_type="always_fail")
        assert result.is_valid is False


@pytest.mark.unit
class TestValidationManagerContextual:
    """Tests for contextual rule support."""

    def test_add_contextual_rule_and_validate(self):
        mgr = ValidationManager()
        mgr.add_contextual_rule(ContextualValidator.required_fields("name"), name="name_required")
        summary = mgr.validate_contextual({})
        assert summary.total > 0
        assert summary.is_valid is False

    def test_contextual_validate_passes(self):
        mgr = ValidationManager()
        mgr.add_contextual_rule(ContextualValidator.required_fields("name"))
        summary = mgr.validate_contextual({"name": "Alice"})
        assert summary.is_valid is True

    def test_contextual_returns_summary(self):
        mgr = ValidationManager()
        summary = mgr.validate_contextual({})
        assert isinstance(summary, ValidationSummary)


@pytest.mark.unit
class TestValidationManagerProfiles:
    """Tests for profile-based validation."""

    def test_create_and_use_profile(self):
        mgr = ValidationManager()

        def check_name(data):
            if not data.get("name"):
                return ValidationIssue(field="name", message="required", severity="error")
            return None

        mgr.create_profile("strict", [("name_check", check_name)])
        summary = mgr.validate_with_profile({}, "strict")
        assert summary.total == 1
        assert summary.is_valid is False

    def test_profile_passing(self):
        mgr = ValidationManager()

        def check_name(data):
            return None  # always passes

        mgr.create_profile("lenient", [("name_check", check_name)])
        summary = mgr.validate_with_profile({"name": "Alice"}, "lenient")
        assert summary.is_valid is True
        assert summary.total == 0

    def test_unknown_profile_returns_empty(self):
        mgr = ValidationManager()
        summary = mgr.validate_with_profile({}, "nonexistent")
        assert summary.total == 0

    def test_create_profile_empty_rules(self):
        mgr = ValidationManager()
        mgr.create_profile("empty")
        summary = mgr.validate_with_profile({}, "empty")
        assert summary.total == 0

    def test_profile_rule_exception_recorded(self):
        mgr = ValidationManager()

        def bad_rule(data):
            raise ValueError("rule failed")

        mgr.create_profile("failing", [("bad_rule", bad_rule)])
        summary = mgr.validate_with_profile({}, "failing")
        # Exception should be caught and recorded as error issue
        assert summary.total == 1
        assert summary.is_valid is False

    def test_profile_rule_returning_non_issue_string(self):
        mgr = ValidationManager()

        def string_rule(data):
            return "some message"

        mgr.create_profile("string_result", [("r", string_rule)])
        summary = mgr.validate_with_profile({}, "string_result")
        # non-None, non-Issue result is wrapped
        assert summary.total == 1


@pytest.mark.unit
class TestValidationManagerStats:
    """Tests for statistics and run tracking."""

    def test_run_count_starts_at_zero(self):
        mgr = ValidationManager()
        assert mgr.run_count == 0

    def test_run_count_increments(self):
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

    def test_summary_empty(self):
        mgr = ValidationManager()
        s = mgr.summary()
        assert s["runs"] == 0

    def test_summary_with_runs(self):
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

    def test_summary_validators_used(self):
        mgr = ValidationManager()
        mgr.validate(1, {"type": "integer"}, validator_type="json_schema")
        s = mgr.summary()
        assert "json_schema" in s["validators_used"]
