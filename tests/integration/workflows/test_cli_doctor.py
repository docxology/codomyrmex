"""CLI Doctor integration tests.

Tests the doctor module's diagnostic checks independently.
"""

import json as json_mod

import pytest


@pytest.mark.integration
class TestCLIDoctor:
    """Tests for cli.doctor diagnostic checks."""

    def test_check_module_imports(self):
        """Module import check finds ≥50 importable modules."""
        from codomyrmex.cli.doctor import check_module_imports

        results = check_module_imports()
        assert len(results) >= 1
        r = results[0]
        assert r.status in ("ok", "warn", "error")
        assert r.details.get("ok", 0) >= 50

    def test_check_pai(self):
        """PAI check returns a result."""
        from codomyrmex.cli.doctor import check_pai

        results = check_pai()
        assert len(results) >= 1
        assert results[0].name == "pai_verify_capabilities"

    def test_check_mcp(self):
        """MCP check returns registry and server results."""
        from codomyrmex.cli.doctor import check_mcp

        results = check_mcp()
        assert len(results) >= 1
        names = [r.name for r in results]
        assert "mcp_tool_registry" in names

    def test_check_rasp(self):
        """RASP check finds complete modules."""
        from codomyrmex.cli.doctor import check_rasp

        results = check_rasp()
        assert len(results) >= 1
        assert results[0].details.get("complete", 0) >= 50

    def test_check_workflows(self):
        """Workflow check finds valid workflow files."""
        from codomyrmex.cli.doctor import check_workflows

        results = check_workflows()
        assert len(results) >= 1
        assert results[0].details.get("valid", 0) >= 5

    def test_run_doctor_default(self):
        """Default doctor run (imports only) returns exit code 0 or 1."""
        from codomyrmex.cli.doctor import run_doctor

        exit_code = run_doctor(output_json=True)
        assert exit_code in (0, 1, 2)

    def test_run_doctor_json_output(self, capsys):
        """JSON output is valid JSON with expected structure."""
        from codomyrmex.cli.doctor import run_doctor

        run_doctor(imports=True, output_json=True)
        captured = capsys.readouterr()
        data = json_mod.loads(captured.out)
        assert "status" in data
        assert "checks" in data
        assert isinstance(data["checks"], list)

    def test_run_doctor_all(self):
        """--all runs all checks without crashing."""
        from codomyrmex.cli.doctor import run_doctor

        exit_code = run_doctor(all_checks=True, output_json=True)
        assert exit_code in (0, 1, 2)
