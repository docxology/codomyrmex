"""What the dependency scan reports when it does not actually run.

``safety check --json`` writes the "1.1" format by default: an object with a
``vulnerabilities`` member. The caller iterated that object as if it were the
older bare list, so a successful scan raised and was swallowed, and a scan that
produced nothing was indistinguishable from a scan that found nothing.

These tests pin the four ways that used to happen silently: the scanner not
being available, exiting non-zero with no output, raising, and returning a
payload the reader cannot understand. The last group is the positive control:
given a report the scanner really emits, a real dependency finding is produced.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
from pathlib import Path

import pytest

from codomyrmex.coding.static_analysis.models import AnalysisType, SeverityLevel
from codomyrmex.coding.static_analysis.static_analyzer import StaticAnalyzer
from codomyrmex.coding.static_analysis.tool_runners import (
    SAFETY_UNAVAILABLE_RULE_ID,
    ToolRunner,
    parse_safety_payload,
)

#: A ``safety check --json`` report in the default "1.1" format, produced by
#: safety 3.8.1's own ``build_json_report`` so the envelope is the real one.
FIXTURE_1_1 = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "safety"
    / "safety_check_1_1.json"
)


def _project(tmp_path: Path) -> Path:
    """A project with one requirement file, so the scan has something to read."""
    (tmp_path / "requirements.txt").write_text("urllib3==1.26.5\n", encoding="utf-8")
    return tmp_path


def _runner(project_root: Path, safety_available: bool = True) -> ToolRunner:
    return ToolRunner({"safety": safety_available}, str(project_root))


def _fake_safety(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str) -> None:
    """Put a real executable named ``safety`` first on PATH.

    This is a real script run as a real subprocess, not a stand-in for the code
    under test; ``monkeypatch.setenv`` is the permitted environment isolation.
    """
    bindir = tmp_path / "fakebin"
    bindir.mkdir(exist_ok=True)
    exe = bindir / "safety"
    exe.write_text(f"#!/bin/sh\n{body}", encoding="utf-8")
    exe.chmod(exe.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}")


def _rule_ids(results) -> list[str]:
    return [r.rule_id for r in results]


# ===========================================================================
# The three ways a scan goes quiet
# ===========================================================================


@pytest.mark.unit
class TestScannerSilenceIsReported:
    """A scan that did not happen must not look like a scan that found nothing."""

    def test_unavailable_tool_is_reported(self, tmp_path):
        project = _project(tmp_path)
        results = _runner(project, safety_available=False).run_safety("probe.py")
        assert _rule_ids(results) == [SAFETY_UNAVAILABLE_RULE_ID]
        assert results[0].category == "security"
        assert "did not run" in results[0].message

    def test_no_requirement_file_is_reported(self, tmp_path):
        results = _runner(tmp_path).run_safety("probe.py")
        assert _rule_ids(results) == [SAFETY_UNAVAILABLE_RULE_ID]

    def test_nonzero_exit_with_empty_output_is_reported(self, tmp_path, monkeypatch):
        project = _project(tmp_path)
        _fake_safety(tmp_path, monkeypatch, "echo 'not authenticated' >&2\nexit 1\n")

        results = _runner(project).run_safety("probe.py")

        assert _rule_ids(results) == [SAFETY_UNAVAILABLE_RULE_ID]
        assert "no report" in results[0].message

    def test_unparseable_output_is_reported(self, tmp_path, monkeypatch):
        project = _project(tmp_path)
        _fake_safety(tmp_path, monkeypatch, "printf 'not json at all'\n")

        results = _runner(project).run_safety("probe.py")

        assert _rule_ids(results) == [SAFETY_UNAVAILABLE_RULE_ID]
        assert "unparseable" in results[0].message

    def test_undecodable_output_is_reported(self, tmp_path, monkeypatch):
        """The backstop: an exception outside the expected subprocess failures."""
        project = _project(tmp_path)
        _fake_safety(tmp_path, monkeypatch, "printf '\\377\\376\\375'\nexit 0\n")

        results = _runner(project).run_safety("probe.py")

        assert _rule_ids(results) == [SAFETY_UNAVAILABLE_RULE_ID]
        assert "raised" in results[0].message

    def test_analysis_reports_the_gap_rather_than_skipping_it(self, tmp_path):
        """The upstream gate used to skip the scan entirely, leaving no trace."""
        project = _project(tmp_path)
        probe = project / "probe.py"
        probe.write_text("VALUE = 1\n", encoding="utf-8")

        analyzer = StaticAnalyzer(project_root=str(project))
        analyzer.tools_available["safety"] = False
        results = analyzer.analyze_file(
            str(probe), analysis_types=[AnalysisType.SECURITY]
        )

        assert SAFETY_UNAVAILABLE_RULE_ID in _rule_ids(results)


# ===========================================================================
# Reading the report the scanner really writes
# ===========================================================================


@pytest.mark.unit
class TestSafetyPayloadReading:
    """Pure reading of a decoded payload, against the real 1.1 shape."""

    def test_captured_1_1_report_yields_a_real_finding(self):
        payload = json.loads(FIXTURE_1_1.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), "the 1.1 format is an object, not a list"

        findings, reason = parse_safety_payload(payload, "requirements.txt")

        assert reason is None
        assert len(findings) == 1
        finding = findings[0]
        assert finding.rule_id == "SAFETY"
        assert finding.category == "security"
        assert "urllib3" in finding.message
        assert finding.suggestion is not None, (
            "parsing a 1.1 report must name the fixed version"
        )
        assert "1.26.19" in finding.suggestion
        assert finding.severity == SeverityLevel.ERROR

    def test_unreported_severity_keeps_the_default(self):
        payload = {
            "vulnerabilities": [{"package_name": "urllib3", "fixed_versions": []}]
        }

        findings, reason = parse_safety_payload(payload, "requirements.txt")

        assert reason is None
        assert findings[0].severity == SeverityLevel.ERROR

    def test_legacy_0_5_list_is_still_read(self):
        payload = [{"package": "urllib3", "safe_version": "1.26.19"}]

        findings, reason = parse_safety_payload(payload, "requirements.txt")

        assert reason is None
        assert len(findings) == 1
        assert "urllib3" in findings[0].message
        assert findings[0].suggestion is not None, (
            "parsing a 0.5 report must name the safe version"
        )
        assert "1.26.19" in findings[0].suggestion

    def test_empty_report_is_clean_not_unavailable(self):
        """Understood-and-empty is a real result; it must not be confused with a gap."""
        findings, reason = parse_safety_payload(
            {"vulnerabilities": []}, "requirements.txt"
        )

        assert findings == []
        assert reason is None

    @pytest.mark.parametrize(
        "payload",
        [
            "a string",
            7,
            None,
            {"report_meta": {}},
            {"vulnerabilities": {"urllib3": "1.26.5"}},
            {"vulnerabilities": ["urllib3==1.26.5"]},
        ],
    )
    def test_payloads_that_cannot_be_read_are_unavailable(self, payload):
        findings, reason = parse_safety_payload(payload, "requirements.txt")

        assert findings == []
        assert reason, f"{payload!r} was accepted as a readable report"


# ===========================================================================
# Controls
# ===========================================================================


@pytest.mark.unit
class TestControls:
    """One control always runs; the other can only run where the scanner works."""

    def test_fixture_control_is_the_operative_one(self):
        """Operative control: a real 1.1 report produces a real finding.

        This one does not depend on the scanner being reachable, so it is the
        control the change is actually justified against.
        """
        payload = json.loads(FIXTURE_1_1.read_text(encoding="utf-8"))
        findings, reason = parse_safety_payload(payload, "requirements.txt")
        assert reason is None
        assert [f.rule_id for f in findings] == ["SAFETY"]

    def test_live_scanner_control(self, tmp_path):
        """Live control against deliberately vulnerable pins.

        Claimed only where safety can genuinely scan. Where it cannot, this test
        records why rather than asserting a green result it did not earn, and the
        fixture control above remains the operative one.
        """
        project = tmp_path
        (project / "requirements.txt").write_text(
            "urllib3==1.26.5\nrequests==2.19.0\n", encoding="utf-8"
        )

        if shutil.which("safety") is None:
            pytest.skip("safety is not installed, so no live scan can be made")

        results = _runner(project).run_safety("requirements.txt")

        if _rule_ids(results) == [SAFETY_UNAVAILABLE_RULE_ID]:
            pytest.skip(f"the live scanner cannot scan here: {results[0].message}")

        assert "SAFETY" in _rule_ids(results)
