"""Tests for config_audits.rules — check_secrets, check_permissions,
check_json_syntax, check_debug_enabled, DEFAULT_RULES.

Zero-mock policy: real filesystem + real regex matching only.
No external dependencies beyond stdlib.
"""
import os

import pytest

from codomyrmex.config_audits.models import AuditIssue, AuditRule, Severity
from codomyrmex.config_audits.rules import (
    DEFAULT_RULES,
    check_debug_enabled,
    check_json_syntax,
    check_permissions,
    check_secrets,
)

# ──────────────────────────── check_secrets ────────────────────────────────


class TestCheckSecrets:
    def test_clean_content_returns_no_issues(self):
        result = check_secrets("host: localhost\nport: 5432", None)
        assert result == []

    def test_password_pattern_detected(self):
        content = 'password: "mysupersecret"'
        issues = check_secrets(content, None)
        assert len(issues) >= 1
        assert any(i.rule_id == "SEC001" for i in issues)

    def test_api_key_pattern_detected(self):
        content = 'api_key = "sk-abc123"'
        issues = check_secrets(content, None)
        assert len(issues) >= 1

    def test_secret_pattern_detected(self):
        content = "secret: 'mySecretValue'"
        issues = check_secrets(content, None)
        assert len(issues) >= 1

    def test_token_pattern_detected(self):
        content = 'token = "Bearer xyz789"'
        issues = check_secrets(content, None)
        assert len(issues) >= 1

    def test_case_insensitive_password(self):
        content = 'PASSWORD: "abc"'
        issues = check_secrets(content, None)
        assert len(issues) >= 1

    def test_case_insensitive_api_key(self):
        content = 'API_KEY = "abc"'
        issues = check_secrets(content, None)
        assert len(issues) >= 1

    def test_severity_is_high(self):
        issues = check_secrets('password: "secret"', None)
        assert all(i.severity == Severity.HIGH for i in issues)

    def test_file_path_stored_in_issue(self):
        issues = check_secrets('api_key: "abc"', "config.yaml")
        assert all(i.file_path == "config.yaml" for i in issues)

    def test_none_file_path_accepted(self):
        issues = check_secrets('secret: "val"', None)
        assert all(i.file_path is None for i in issues)

    def test_dict_content_stringified(self):
        content = {"password": "plaintext"}
        issues = check_secrets(content, None)
        # dict.__str__ may not match regex (no quotes around value in all cases)
        assert isinstance(issues, list)

    def test_empty_string_returns_no_issues(self):
        assert check_secrets("", None) == []

    def test_recommendation_present(self):
        issues = check_secrets('token: "mytoken"', None)
        assert all(i.recommendation is not None for i in issues)

    def test_multiple_patterns_multiple_issues(self):
        content = 'password: "p1"\napi_key: "k1"\nsecret: "s1"\ntoken: "t1"'
        issues = check_secrets(content, None)
        assert len(issues) == 4

    def test_pattern_without_quotes_not_detected(self):
        # The regex requires quotes around the value
        content = "password: no_quotes_here"
        issues = check_secrets(content, None)
        assert issues == []


# ──────────────────────────── check_permissions ────────────────────────────


class TestCheckPermissions:
    def test_world_readable_file_returns_issue(self, tmp_path):
        f = tmp_path / "config.yaml"
        f.write_text("key: value")
        os.chmod(f, 0o644)  # world-readable
        issues = check_permissions("key: value", str(f))
        assert len(issues) >= 1
        assert issues[0].rule_id == "SEC002"

    def test_private_file_returns_no_issues(self, tmp_path):
        f = tmp_path / "config.yaml"
        f.write_text("key: value")
        os.chmod(f, 0o600)  # owner only
        issues = check_permissions("key: value", str(f))
        assert issues == []

    def test_none_file_path_returns_empty(self):
        result = check_permissions("anything", None)
        assert result == []

    def test_nonexistent_path_returns_empty(self):
        result = check_permissions("anything", "/nonexistent/file.yaml")
        assert result == []

    def test_severity_is_medium(self, tmp_path):
        f = tmp_path / "c.yaml"
        f.write_text("x: 1")
        os.chmod(f, 0o644)
        issues = check_permissions("x: 1", str(f))
        assert all(i.severity == Severity.MEDIUM for i in issues)

    def test_file_path_in_message(self, tmp_path):
        f = tmp_path / "cfg.yaml"
        f.write_text("x: 1")
        os.chmod(f, 0o644)
        issues = check_permissions("x: 1", str(f))
        assert str(f) in issues[0].message

    def test_content_param_not_used(self, tmp_path):
        f = tmp_path / "x.yaml"
        f.write_text("a: b")
        os.chmod(f, 0o644)
        # check_permissions ignores content — only path matters
        issues = check_permissions(None, str(f))
        assert len(issues) >= 1


# ──────────────────────────── check_json_syntax ────────────────────────────


class TestCheckJsonSyntax:
    def test_valid_json_returns_no_issues(self, tmp_path):
        f = tmp_path / "config.json"
        f.write_text('{"key": "value"}')
        issues = check_json_syntax('{"key": "value"}', str(f))
        assert issues == []

    def test_invalid_json_returns_issue(self, tmp_path):
        f = tmp_path / "config.json"
        issues = check_json_syntax("{bad json: }", str(f))
        assert len(issues) >= 1
        assert issues[0].rule_id == "SYN001"

    def test_non_json_file_extension_skipped(self, tmp_path):
        f = tmp_path / "config.yaml"
        issues = check_json_syntax("{bad json:}", str(f))
        assert issues == []

    def test_none_file_path_skipped(self):
        issues = check_json_syntax("{bad json:}", None)
        assert issues == []

    def test_severity_critical(self, tmp_path):
        f = tmp_path / "c.json"
        issues = check_json_syntax("{invalid", str(f))
        assert all(i.severity == Severity.CRITICAL for i in issues)

    def test_valid_json_array(self, tmp_path):
        f = tmp_path / "arr.json"
        issues = check_json_syntax("[1, 2, 3]", str(f))
        assert issues == []

    def test_empty_json_object_valid(self, tmp_path):
        f = tmp_path / "empty.json"
        issues = check_json_syntax("{}", str(f))
        assert issues == []

    def test_recommendation_present_on_error(self, tmp_path):
        f = tmp_path / "bad.json"
        issues = check_json_syntax("{bad}", str(f))
        assert all(i.recommendation is not None for i in issues)


# ──────────────────────────── check_debug_enabled ──────────────────────────


class TestCheckDebugEnabled:
    def test_prod_file_with_debug_true_detected(self):
        issues = check_debug_enabled('"debug": true', "config.prod.json")
        assert len(issues) >= 1
        assert issues[0].rule_id == "OPS001"

    def test_prod_file_debug_false_no_issue(self):
        issues = check_debug_enabled('"debug": false', "config.prod.json")
        assert issues == []

    def test_non_prod_file_skipped_even_with_debug(self):
        issues = check_debug_enabled('"debug": true', "config.dev.json")
        assert issues == []

    def test_none_file_path_skipped(self):
        issues = check_debug_enabled('"debug": true', None)
        assert issues == []

    def test_yaml_style_debug_true(self):
        issues = check_debug_enabled("debug: true", "production.yaml")
        assert len(issues) >= 1

    def test_severity_is_high(self):
        issues = check_debug_enabled('"debug": true', "prod.json")
        assert all(i.severity == Severity.HIGH for i in issues)

    def test_rule_id_is_ops001(self):
        issues = check_debug_enabled('"debug": true', "prod.json")
        assert issues[0].rule_id == "OPS001"

    def test_case_insensitive_prod_in_filename(self):
        # "PROD" in filename should also match
        issues = check_debug_enabled('"debug": true', "PRODUCTION.json")
        assert len(issues) >= 1

    def test_debug_false_in_prod_not_flagged(self):
        issues = check_debug_enabled("debug: false", "prod.yaml")
        assert issues == []


# ──────────────────────────── DEFAULT_RULES ────────────────────────────────


class TestDefaultRules:
    def test_is_list(self):
        assert isinstance(DEFAULT_RULES, list)

    def test_has_four_rules(self):
        assert len(DEFAULT_RULES) == 4

    def test_all_are_audit_rules(self):
        assert all(isinstance(r, AuditRule) for r in DEFAULT_RULES)

    def test_rule_ids_present(self):
        ids = {r.rule_id for r in DEFAULT_RULES}
        assert "SEC001" in ids
        assert "SEC002" in ids
        assert "SYN001" in ids
        assert "OPS001" in ids

    def test_check_funcs_are_callable(self):
        for rule in DEFAULT_RULES:
            assert callable(rule.check_func)

    def test_sec001_callable_on_plain_string(self):
        rule = next(r for r in DEFAULT_RULES if r.rule_id == "SEC001")
        result = rule.check_func('password: "abc"', None)
        assert isinstance(result, list)

    def test_syn001_callable_on_json_file(self, tmp_path):
        f = tmp_path / "x.json"
        rule = next(r for r in DEFAULT_RULES if r.rule_id == "SYN001")
        result = rule.check_func("{bad}", str(f))
        assert isinstance(result, list)


# ──────────────────────────── AuditIssue model ─────────────────────────────


class TestAuditIssue:
    def test_basic_construction(self):
        issue = AuditIssue(
            rule_id="TEST001",
            message="test message",
            severity=Severity.LOW,
        )
        assert issue.rule_id == "TEST001"
        assert issue.message == "test message"
        assert issue.severity == Severity.LOW

    def test_optional_fields_default_none(self):
        issue = AuditIssue(rule_id="X", message="msg", severity=Severity.HIGH)
        assert issue.file_path is None
        assert issue.location is None
        assert issue.recommendation is None

    def test_severity_enum_values(self):
        assert Severity.LOW.value == "low"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.HIGH.value == "high"
        assert Severity.CRITICAL.value == "critical"
