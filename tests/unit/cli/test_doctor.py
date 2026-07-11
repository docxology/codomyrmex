"""Unit tests for codomyrmex.cli.doctor module.

Tests the CLI doctor self-diagnostic system: CheckResult, individual check
functions, and the run_doctor orchestrator.
"""

from __future__ import annotations

import json

import pytest

from codomyrmex.cli.doctor import (
    CheckResult,
    check_module_imports,
    check_workflows,
    run_doctor,
)


@pytest.mark.unit
class TestCheckResult:
    """Tests for the CheckResult diagnostic result type."""

    def test_default_status_is_ok(self):
        """CheckResult defaults to OK status."""
        cr = CheckResult("test_check")
        assert cr.name == "test_check"
        assert cr.status == CheckResult.OK
        assert cr.message == ""
        assert cr.details == {}

    def test_explicit_status_and_message(self):
        """CheckResult stores explicit status and message."""
        cr = CheckResult("mod_check", CheckResult.ERROR, "something broke")
        assert cr.status == CheckResult.ERROR
        assert cr.message == "something broke"

    def test_details_preserved(self):
        """CheckResult stores arbitrary details dict."""
        details = {"total": 10, "failed": ["a", "b"]}
        cr = CheckResult("detail_check", details=details)
        assert cr.details == details
        assert cr.details["total"] == 10

    def test_details_defaults_to_empty_dict(self):
        """CheckResult.details defaults to empty dict when None."""
        cr = CheckResult("no_details", details=None)
        assert cr.details == {}

    def test_to_dict_minimal(self):
        """to_dict with OK status, no message, no details returns name+status only."""
        cr = CheckResult("minimal")
        d = cr.to_dict()
        assert d == {"name": "minimal", "status": "ok"}
        assert "message" not in d
        assert "details" not in d

    def test_to_dict_with_message(self):
        """to_dict includes message when set."""
        cr = CheckResult("msg_check", message="all good")
        d = cr.to_dict()
        assert d["message"] == "all good"

    def test_to_dict_with_details(self):
        """to_dict includes details when non-empty."""
        cr = CheckResult("det_check", details={"count": 42})
        d = cr.to_dict()
        assert d["details"] == {"count": 42}

    def test_to_dict_full(self):
        """to_dict with all fields populated."""
        cr = CheckResult("full", CheckResult.WARN, "partial", {"ok": 5, "fail": 2})
        d = cr.to_dict()
        assert d["name"] == "full"
        assert d["status"] == "warn"
        assert d["message"] == "partial"
        assert d["details"]["ok"] == 5

    def test_status_constants(self):
        """Status constants have expected values."""
        assert CheckResult.OK == "ok"
        assert CheckResult.WARN == "warn"
        assert CheckResult.ERROR == "error"

    def test_slots_defined(self):
        """CheckResult uses __slots__ for memory efficiency."""
        assert "__slots__" in dir(CheckResult) or hasattr(CheckResult, "__slots__")
        cr = CheckResult("slots_test")
        with pytest.raises(AttributeError):
            cr.nonexistent_attr = "should fail"


@pytest.mark.unit
class TestCheckModuleImports:
    """Tests for the check_module_imports function."""

    def test_returns_list_of_check_results(self):
        """check_module_imports returns a non-empty list of CheckResult."""
        results = check_module_imports()
        assert isinstance(results, list)
        assert len(results) >= 1
        assert all(isinstance(r, CheckResult) for r in results)

    def test_result_has_module_imports_name(self):
        """The primary result is named 'module_imports' or 'module_discovery'."""
        results = check_module_imports()
        names = {r.name for r in results}
        assert names & {"module_imports", "module_discovery"}

    def test_details_contain_counts(self):
        """module_imports result details contain total and ok counts."""
        results = check_module_imports()
        for r in results:
            if r.name == "module_imports":
                assert "total" in r.details
                assert "ok" in r.details
                assert r.details["ok"] >= 1
                break


@pytest.mark.unit
class TestCheckWorkflows:
    """Tests for the check_workflows function."""

    def test_returns_list_of_check_results(self):
        """check_workflows returns a list of CheckResult."""
        results = check_workflows()
        assert isinstance(results, list)
        assert len(results) >= 1
        assert all(isinstance(r, CheckResult) for r in results)


def _extract_json(raw: str) -> dict:
    """Extract the first JSON object from raw output that may contain log lines."""
    start = raw.find("{")
    if start == -1:
        raise ValueError("No JSON object found in output")
    # Find matching closing brace by parsing from start
    return json.loads(raw[start:])


@pytest.mark.unit
class TestRunDoctor:
    """Tests for the run_doctor orchestrator."""

    def test_default_runs_imports(self, capsys):
        """Default run_doctor (no flags) runs module imports check."""
        result = run_doctor()
        assert isinstance(result, bool)

    def test_json_output(self, capsys):
        """run_doctor with output_json=True produces valid JSON."""
        run_doctor(imports=True, output_json=True)
        captured = capsys.readouterr()
        data = _extract_json(captured.out)
        assert "status" in data
        assert "checks" in data
        assert isinstance(data["checks"], list)

    def test_json_output_status_field(self, capsys):
        """JSON output status is one of ok, warn, error."""
        run_doctor(imports=True, output_json=True)
        captured = capsys.readouterr()
        data = _extract_json(captured.out)
        assert data["status"] in ("ok", "warn", "error")

    def test_text_output_contains_doctor_header(self, capsys):
        """Text output contains the Doctor header."""
        run_doctor(imports=True)
        captured = capsys.readouterr()
        assert "Doctor" in captured.out

    def test_all_checks_flag(self, capsys):
        """run_doctor with all_checks=True runs multiple checks."""
        run_doctor(all_checks=True, output_json=True)
        captured = capsys.readouterr()
        data = _extract_json(captured.out)
        # all_checks should run at least imports + workflows + rasp
        assert len(data["checks"]) >= 3
