"""Tests for release MCP tools."""

from __future__ import annotations


class TestReleaseValidate:
    """Tests for release_validate MCP tool."""

    def test_validate_all_passing(self):
        from codomyrmex.release.mcp_tools import release_validate

        result = release_validate(
            version="2.0.0",
            test_failures=0,
            test_total=100,
            coverage_overall=70.0,
            cve_count=0,
            secrets_found=0,
            docs_complete=True,
        )
        assert result["status"] == "success"
        assert result["certified"] is True
        assert result["version"] == "2.0.0"
        assert result["pass_rate"] > 0
        assert len(result["blockers"]) == 0

    def test_validate_with_failures(self):
        from codomyrmex.release.mcp_tools import release_validate

        result = release_validate(
            version="1.0.0",
            test_failures=5,
            test_total=100,
            coverage_overall=30.0,
            cve_count=2,
            secrets_found=1,
            docs_complete=False,
        )
        assert result["status"] == "success"
        assert result["certified"] is False
        assert len(result["blockers"]) > 0

    def test_validate_minimal_args(self):
        from codomyrmex.release.mcp_tools import release_validate

        result = release_validate()
        assert result["status"] == "success"
        assert "certified" in result
        assert "checks" in result


class TestReleaseBuild:
    """Tests for release_build MCP tool."""

    def test_build_success(self):
        from codomyrmex.release.mcp_tools import release_build

        result = release_build(name="testpkg", version="1.2.3")
        assert result["status"] == "success"
        assert result["success"] is True
        assert len(result["artifacts"]) == 2
        filenames = [a["filename"] for a in result["artifacts"]]
        assert any("testpkg-1.2.3" in f for f in filenames)

    def test_build_missing_name(self):
        from codomyrmex.release.mcp_tools import release_build

        result = release_build(name="", version="1.0.0")
        assert result["status"] == "success"
        assert result["success"] is False
        assert len(result["warnings"]) > 0


class TestReleaseCertificationReport:
    """Tests for release_certification_report MCP tool."""

    def test_report_certified(self):
        from codomyrmex.release.mcp_tools import release_certification_report

        result = release_certification_report(
            version="3.0.0",
            test_failures=0,
            test_total=500,
            coverage_overall=80.0,
        )
        assert result["status"] == "success"
        assert result["certified"] is True
        assert "markdown" in result
        assert "3.0.0" in result["markdown"]

    def test_report_not_certified(self):
        from codomyrmex.release.mcp_tools import release_certification_report

        result = release_certification_report(
            version="1.0.0",
            test_failures=10,
            test_total=100,
            coverage_overall=40.0,
        )
        assert result["status"] == "success"
        assert result["certified"] is False
