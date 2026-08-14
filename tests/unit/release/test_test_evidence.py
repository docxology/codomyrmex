"""Regression tests for source-bound skipped-test and warning evidence."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from codomyrmex.release.test_evidence import (
    EvidenceFormatError,
    ReleaseTestEvidence,
    SkippedTest,
    WarningEvent,
    parse_coverage_xml,
    parse_junit_xml,
    run_release_test_evidence,
)


def _git_repo(
    root: Path, *, test_source: str = "def test_passes():\n    assert True\n"
) -> Path:
    test_path = root / f"test_sample_{root.name}.py"
    test_path.write_text(test_source, encoding="utf-8")
    (root / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\nasyncio_default_fixture_loop_scope = "function"\n',
        encoding="utf-8",
    )
    (root / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "init", "--quiet"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.name", "release-test"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "config",
            "user.email",
            "release-test@example.invalid",
        ],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "add",
            test_path.name,
            "pyproject.toml",
            ".gitignore",
        ],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "commit", "--quiet", "-m", "fixture"],
        check=True,
    )
    return root


def _test_path(root: Path) -> str:
    return next(root.glob("test_sample_*.py")).name


@pytest.mark.unit
def test_parse_junit_preserves_skips_and_outcomes(tmp_path: Path):
    report = tmp_path / "junit.xml"
    report.write_text(
        """<?xml version="1.0"?>
<testsuites>
  <testsuite name="pytest" tests="3" failures="1" errors="0" skipped="1">
    <testcase classname="sample" name="pass" />
    <testcase classname="sample" name="skip"><skipped message="provider unavailable" /></testcase>
    <testcase classname="sample" name="fail"><failure message="broken" /></testcase>
  </testsuite>
</testsuites>
""",
        encoding="utf-8",
    )

    evidence = parse_junit_xml(report)

    assert (evidence.total, evidence.failures, evidence.errors, evidence.skipped) == (
        3,
        1,
        0,
        1,
    )
    assert evidence.skipped_tests == (
        SkippedTest("sample::skip", "provider unavailable"),
    )
    assert evidence.failure_tests == ("sample::fail",)


@pytest.mark.unit
def test_parse_junit_rejects_stale_or_inconsistent_counts(tmp_path: Path):
    report = tmp_path / "junit.xml"
    report.write_text(
        '<testsuite tests="2" failures="0" errors="0" skipped="0">'
        '<testcase classname="sample" name="only" />'
        "</testsuite>",
        encoding="utf-8",
    )

    with pytest.raises(EvidenceFormatError, match="does not match"):
        parse_junit_xml(report)


@pytest.mark.unit
def test_parse_junit_requires_detail_for_declared_outcomes(tmp_path: Path):
    report = tmp_path / "junit.xml"
    report.write_text(
        '<testsuite tests="1" failures="0" errors="0" skipped="1" />',
        encoding="utf-8",
    )

    with pytest.raises(EvidenceFormatError, match="no testcase evidence"):
        parse_junit_xml(report)


@pytest.mark.unit
def test_parse_junit_rejects_empty_testcase_evidence(tmp_path: Path):
    report = tmp_path / "junit.xml"
    report.write_text(
        '<testsuite tests="0" failures="0" errors="0" skipped="0" />',
        encoding="utf-8",
    )

    with pytest.raises(EvidenceFormatError, match="no testcase evidence"):
        parse_junit_xml(report)


@pytest.mark.unit
def test_parse_junit_rejects_skips_without_reasons(tmp_path: Path):
    report = tmp_path / "junit.xml"
    report.write_text(
        '<testsuite tests="1" failures="0" errors="0" skipped="1">'
        '<testcase classname="sample" name="skip"><skipped /></testcase>'
        "</testsuite>",
        encoding="utf-8",
    )

    with pytest.raises(EvidenceFormatError, match="no reason"):
        parse_junit_xml(report)


@pytest.mark.unit
def test_parse_junit_preserves_text_skip_reason(tmp_path: Path):
    report = tmp_path / "junit.xml"
    report.write_text(
        '<testsuite tests="1" failures="0" errors="0" skipped="1">'
        '<testcase classname="sample" name="skip">'
        "<skipped>provider unavailable</skipped>"
        "</testcase></testsuite>",
        encoding="utf-8",
    )

    evidence = parse_junit_xml(report)

    assert evidence.skipped_tests == (
        SkippedTest("sample::skip", "provider unavailable"),
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("xml", "message"),
    [
        (
            '<testsuite tests="1"><testcase status="skipped" '
            'classname="sample" name="ambiguous" /></testsuite>',
            "without a skipped element",
        ),
        (
            '<testsuite tests="1"><testcase><skipped /></testcase></testsuite>',
            "no identifying attributes",
        ),
        (
            '<testsuite tests="1"><testcase classname="sample" name="bad">'
            "<rerunFailure /></testcase></testsuite>",
            "unsupported outcome",
        ),
    ],
)
def test_parse_junit_rejects_ambiguous_outcomes(xml: str, message: str, tmp_path: Path):
    report = tmp_path / "junit.xml"
    report.write_text(xml, encoding="utf-8")

    with pytest.raises(EvidenceFormatError, match=message):
        parse_junit_xml(report)


@pytest.mark.unit
def test_parse_junit_rejects_dtd_entity_input(tmp_path: Path):
    report = tmp_path / "junit.xml"
    report.write_text(
        "<!DOCTYPE testsuite [<!ENTITY xxe 'blocked'>]>"
        '<testsuite tests="1"><testcase classname="sample" name="pass">'
        "<system-out>&xxe;</system-out></testcase></testsuite>",
        encoding="utf-8",
    )

    with pytest.raises(EvidenceFormatError, match="DTD/entity"):
        parse_junit_xml(report)


@pytest.mark.unit
def test_parse_coverage_validates_measured_line_rate(tmp_path: Path):
    report = tmp_path / "coverage.xml"
    report.write_text(
        '<coverage line-rate="0.75" lines-covered="3" lines-valid="4" />',
        encoding="utf-8",
    )

    evidence = parse_coverage_xml(report)

    assert evidence.line_rate_percent == pytest.approx(75.0)
    assert evidence.lines_covered == 3
    assert evidence.lines_valid == 4


@pytest.mark.unit
def test_parse_coverage_rejects_inconsistent_counts(tmp_path: Path):
    report = tmp_path / "coverage.xml"
    report.write_text(
        '<coverage line-rate="0.75" lines-covered="2" lines-valid="4" />',
        encoding="utf-8",
    )

    with pytest.raises(EvidenceFormatError, match="does not match"):
        parse_coverage_xml(report)


@pytest.mark.unit
def test_release_evidence_fails_closed_on_warning_and_skip_budget():
    evidence = ReleaseTestEvidence(
        source_revision="a" * 40,
        source_tree="b" * 40,
        source_clean=True,
        dirty_paths=(),
        test_paths=("tests/unit",),
        pytest_args=(),
        command=("python", "-m", "pytest"),
        exit_code=0,
        total=2,
        failures=0,
        errors=0,
        skipped=1,
        skipped_tests=(SkippedTest("test_sample.py::test_skip", "offline"),),
        warnings=(
            WarningEvent(
                message="deprecated",
                category="DeprecationWarning",
                filename="test_sample.py",
                lineno=4,
                nodeid="test_sample.py::test_pass",
                when="runtest",
            ),
        ),
        max_skips=0,
        max_warnings=0,
        require_clean_source=True,
        junit_report_sha256="a" * 64,
        profile="local",
    )

    assert evidence.certified is False
    assert any("skipped tests" in blocker for blocker in evidence.blockers)
    assert any("warnings" in blocker for blocker in evidence.blockers)


@pytest.mark.unit
def test_run_source_bound_receipt_is_current_and_clean(tmp_path: Path):
    root = _git_repo(
        tmp_path,
        test_source=(
            "from pathlib import Path\n\n"
            "def test_passes():\n"
            "    Path('coverage.xml').write_text(\n"
            '        \'<coverage line-rate="0.6" lines-covered="3" '
            "lines-valid=\"5\" />', encoding='utf-8'\n"
            "    )\n"
        ),
    )
    receipt = tmp_path / "release-test-evidence.json"

    evidence = run_release_test_evidence(
        root,
        (_test_path(root),),
        pytest_args=("-q",),
        receipt_path=receipt,
        max_skips=0,
        max_warnings=0,
        allowed_output_paths=("coverage.xml",),
        required_output_paths=("coverage.xml",),
        profile="release",
        coverage_report_path="coverage.xml",
        coverage_floor_percent=60,
    )

    assert evidence.certified is True
    assert evidence.total == 1
    assert evidence.skipped == 0
    assert evidence.warnings == ()
    raw = json.loads(receipt.read_text(encoding="utf-8"))
    assert raw["source"]["revision"] == evidence.source_revision
    assert raw["source"]["tree"] == evidence.source_tree
    assert raw["schema_version"] == 2
    assert raw["profile"] == "release"
    assert len(raw["results"]["junit_report_sha256"]) == 64
    assert raw["coverage"]["line_rate_percent"] == pytest.approx(60.0)
    assert len(raw["coverage"]["sha256"]) == 64
    assert "no:benchmark" in raw["command"]
    assert any(item == "--junitxml=<temporary-junit.xml>" for item in raw["command"])
    assert all("pytest-of-" not in item for item in raw["command"])
    assert raw["results"] == {
        "errors": 0,
        "failures": 0,
        "junit_report_sha256": evidence.junit_report_sha256,
        "skipped": 0,
        "total": 1,
    }


@pytest.mark.unit
def test_run_source_bound_records_warning_events(tmp_path: Path):
    root = _git_repo(
        tmp_path,
        test_source=(
            "import warnings\n\n"
            "def test_warns():\n"
            '    warnings.warn("fixture warning", UserWarning)\n'
        ),
    )

    evidence = run_release_test_evidence(
        root,
        (_test_path(root),),
        pytest_args=("-q",),
        max_skips=0,
        max_warnings=0,
    )

    assert evidence.certified is False
    assert len(evidence.warnings) == 1
    assert evidence.warnings[0].message == "fixture warning"
    assert evidence.warnings[0].category == "UserWarning"
    assert evidence.warnings[0].nodeid.endswith("::test_warns")


@pytest.mark.unit
def test_run_source_bound_rejects_dirty_source_without_running_tests(tmp_path: Path):
    root = _git_repo(tmp_path)
    test_path = root / _test_path(root)
    test_path.write_text("def test_passes():\n    assert False\n", encoding="utf-8")

    evidence = run_release_test_evidence(
        root,
        (_test_path(root),),
        max_skips=0,
        max_warnings=0,
        profile="release",
    )

    assert evidence.certified is False
    assert evidence.source_clean is False
    assert _test_path(root) in evidence.dirty_paths
    assert evidence.total == 0
    assert any("source checkout is dirty" in blocker for blocker in evidence.blockers)


@pytest.mark.unit
def test_run_source_bound_rejects_policy_override_args(tmp_path: Path):
    root = _git_repo(tmp_path)

    evidence = run_release_test_evidence(
        root,
        (_test_path(root),),
        pytest_args=("--junit-xml=stale.xml", "--disable-warnings"),
        max_skips=0,
        max_warnings=0,
    )

    assert evidence.certified is False
    assert evidence.total == 0
    assert any("cannot override" in blocker for blocker in evidence.blockers)


@pytest.mark.unit
def test_local_profile_runs_on_dirty_source_and_identifies_profile(tmp_path: Path):
    root = _git_repo(tmp_path)
    (root / _test_path(root)).write_text(
        "# local developer edit\ndef test_passes():\n    assert True\n",
        encoding="utf-8",
    )

    evidence = run_release_test_evidence(
        root,
        (_test_path(root),),
        pytest_args=("-q",),
        max_skips=0,
        max_warnings=0,
    )

    assert evidence.profile == "local"
    assert evidence.source_clean is False
    assert evidence.total == 1
    assert evidence.certified is False
    assert evidence.to_dict()["profile"] == "local"


@pytest.mark.unit
def test_release_profile_requires_fresh_parseable_coverage_report(tmp_path: Path):
    root = _git_repo(tmp_path)

    evidence = run_release_test_evidence(
        root,
        (_test_path(root),),
        pytest_args=("-q",),
        max_skips=0,
        max_warnings=0,
        profile="release",
        coverage_report_path="coverage.xml",
        coverage_floor_percent=60,
    )

    assert evidence.total == 1
    assert evidence.coverage_line_rate_percent is None
    assert evidence.certified is False
    assert any("coverage report is missing" in item for item in evidence.blockers)


@pytest.mark.unit
def test_allowed_output_cannot_whitelist_tracked_source(tmp_path: Path):
    root = _git_repo(tmp_path)

    evidence = run_release_test_evidence(
        root,
        (_test_path(root),),
        allowed_output_paths=(_test_path(root),),
        max_skips=0,
        max_warnings=0,
    )

    assert evidence.total == 0
    assert any("overlaps tracked source" in item for item in evidence.blockers)
    assert evidence.certified is False


@pytest.mark.unit
def test_release_profile_rejects_nonzero_warning_budget(tmp_path: Path):
    root = _git_repo(tmp_path)

    evidence = run_release_test_evidence(
        root,
        (_test_path(root),),
        profile="release",
        max_skips=0,
        max_warnings=1,
    )

    assert evidence.total == 0
    assert any("max_warnings=0" in error for error in evidence.errors_detail)
    assert evidence.certified is False


@pytest.mark.unit
def test_required_output_must_be_refreshed(tmp_path: Path):
    root = _git_repo(tmp_path)
    (root / "coverage.xml").write_text("stale", encoding="utf-8")

    evidence = run_release_test_evidence(
        root,
        (_test_path(root),),
        pytest_args=("-q",),
        required_output_paths=("coverage.xml",),
        max_skips=0,
        max_warnings=0,
    )

    assert evidence.total == 1
    assert evidence.fresh_output_paths == ()
    assert any("not refreshed" in error for error in evidence.errors_detail)
    assert evidence.certified is False


@pytest.mark.unit
def test_required_output_is_recorded_when_created_by_test(tmp_path: Path):
    root = _git_repo(
        tmp_path,
        test_source=(
            "from pathlib import Path\n\n"
            "def test_writes_report():\n"
            '    Path("coverage.xml").write_text("fresh", encoding="utf-8")\n'
        ),
    )

    evidence = run_release_test_evidence(
        root,
        (_test_path(root),),
        pytest_args=("-q",),
        required_output_paths=("coverage.xml",),
        max_skips=0,
        max_warnings=0,
    )

    assert evidence.certified is True
    assert evidence.fresh_output_paths == ("coverage.xml",)
    assert evidence.allowed_output_paths == ("coverage.xml",)


@pytest.mark.unit
def test_missing_junit_report_cannot_become_green(tmp_path: Path):
    root = _git_repo(tmp_path)

    evidence = run_release_test_evidence(
        root,
        (_test_path(root),),
        pytest_args=("--definitely-not-a-pytest-option",),
        max_skips=0,
        max_warnings=0,
    )

    assert evidence.total == 0
    assert any("JUnit report is missing" in error for error in evidence.errors_detail)
    assert evidence.certified is False


@pytest.mark.unit
def test_run_source_bound_rejects_source_changes_during_tests(tmp_path: Path):
    root = _git_repo(
        tmp_path,
        test_source=(
            "from pathlib import Path\n\n"
            "def test_mutates_checkout():\n"
            '    Path("unexpected-output.txt").write_text("changed", encoding="utf-8")\n'
        ),
    )

    evidence = run_release_test_evidence(
        root,
        (_test_path(root),),
        pytest_args=("-q",),
        max_skips=0,
        max_warnings=0,
    )

    assert evidence.total == 1
    assert evidence.certified is False
    assert "unexpected-output.txt" in evidence.dirty_paths
    assert any(
        "changed during the test run" in blocker for blocker in evidence.blockers
    )


@pytest.mark.unit
def test_release_and_ci_workflows_use_blocking_evidence_paths():
    repo_root = Path(__file__).resolve().parents[3]
    release_workflow = (repo_root / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8"
    )
    ci_workflow = (repo_root / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    integration_workflow = (
        repo_root / ".github" / "workflows" / "ci-integration.yml"
    ).read_text(encoding="utf-8")

    assert "codomyrmex.release.test_evidence" in release_workflow
    assert "--require-clean" in release_workflow
    assert "--max-skips 600" in release_workflow
    assert "--max-warnings 0" in release_workflow
    assert "--profile release" in release_workflow
    assert "--required-output-path coverage.xml" in release_workflow
    assert "--coverage-report coverage.xml" in release_workflow
    assert "--coverage-floor 60" in release_workflow
    assert "release-test-evidence.json" in release_workflow
    assert "skipped_tests=$(grep -roh" in ci_workflow
    assert "passed=$((total_tests - failed_tests - error_tests - skipped_tests))" in (
        ci_workflow
    )
    assert "|| true" not in integration_workflow
    assert "-W error" in integration_workflow
    assert "junit-integration.xml" in integration_workflow
