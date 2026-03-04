"""Tests for config_audits MCP tools."""

import json
import os
import tempfile

from codomyrmex.config_audits.mcp_tools import (
    config_audits_audit_directory,
    config_audits_audit_file,
    config_audits_generate_report,
)


class TestConfigAuditsAuditFile:
    def test_returns_dict_with_status(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"key": "value"}, f)
            f.flush()
            result = config_audits_audit_file(file_path=f.name)
        os.unlink(f.name)
        assert isinstance(result, dict)
        assert "status" in result

    def test_clean_file_is_compliant(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"app_name": "test"}, f)
            f.flush()
            result = config_audits_audit_file(file_path=f.name)
        os.unlink(f.name)
        assert result["status"] == "success"
        assert result["is_compliant"] is True

    def test_missing_file_returns_issues(self):
        result = config_audits_audit_file(file_path="/nonexistent/path/config.json")
        assert result["status"] == "success"
        assert result["issue_count"] > 0

    def test_file_with_secret_detected(self):
        # The auditor regex matches `password = "value"` or `password: "value"` patterns
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write('password = "supersecret123"\n')
            f.flush()
            result = config_audits_audit_file(file_path=f.name)
        os.unlink(f.name)
        assert result["status"] == "success"
        assert result["issue_count"] > 0


class TestConfigAuditsAuditDirectory:
    def test_returns_dict_with_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = config_audits_audit_directory(directory_path=tmpdir)
        assert isinstance(result, dict)
        assert result["status"] == "success"

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = config_audits_audit_directory(directory_path=tmpdir)
        assert result["files_audited"] == 0
        assert result["total_issues"] == 0

    def test_directory_with_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "test.json")
            with open(config_file, "w") as f:
                json.dump({"name": "test"}, f)
            result = config_audits_audit_directory(directory_path=tmpdir)
        assert result["files_audited"] == 1


class TestConfigAuditsGenerateReport:
    def test_returns_dict_with_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = config_audits_generate_report(directory_path=tmpdir)
        assert isinstance(result, dict)
        assert result["status"] == "success"

    def test_report_is_string(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = config_audits_generate_report(directory_path=tmpdir)
        assert isinstance(result["report"], str)

    def test_report_with_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "app.json")
            with open(config_file, "w") as f:
                json.dump({"debug": True}, f)
            result = config_audits_generate_report(directory_path=tmpdir)
        assert result["status"] == "success"
        assert "Audit Report" in result["report"] or "No audit" in result["report"]
