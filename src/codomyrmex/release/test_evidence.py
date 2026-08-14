"""Source-bound pytest evidence for fail-closed release gates.

The release workflow must not accept hand-entered test counts or infer that a
green process exit means that all requested tests ran cleanly.  This module
runs the selected pytest command, collects warning events, parses the JUnit
receipt, binds the result to the current Git source identity, and emits one
machine-readable receipt for the release job.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import subprocess  # nosec B404
import sys
import tempfile
import time
import warnings
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from defusedxml import ElementTree as ET

EvidenceProfile = Literal["local", "release"]
_EVIDENCE_PROFILES = frozenset(("local", "release"))


class EvidenceFormatError(ValueError):
    """Raised when a test-evidence input is absent or internally inconsistent."""


@dataclass(frozen=True)
class SkippedTest:
    """One skipped test recorded in a JUnit receipt."""

    nodeid: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"nodeid": self.nodeid, "reason": self.reason}


@dataclass(frozen=True)
class WarningEvent:
    """One warning event observed by pytest's warning hook."""

    message: str
    category: str
    filename: str
    lineno: int
    nodeid: str
    when: str

    def to_dict(self) -> dict[str, str | int]:
        return {
            "message": self.message,
            "category": self.category,
            "filename": self.filename,
            "lineno": self.lineno,
            "nodeid": self.nodeid,
            "when": self.when,
        }


@dataclass(frozen=True)
class JUnitEvidence:
    """Parsed test outcomes from a JUnit XML report."""

    total: int
    failures: int
    errors: int
    skipped: int
    skipped_tests: tuple[SkippedTest, ...] = ()
    failure_tests: tuple[str, ...] = ()
    error_tests: tuple[str, ...] = ()


@dataclass(frozen=True)
class CoverageEvidence:
    """Validated coverage XML evidence expressed in percentage points."""

    line_rate_percent: float
    lines_covered: int | None = None
    lines_valid: int | None = None
    version: str | None = None


@dataclass(frozen=True)
class ReleaseTestEvidence:
    """Complete source-bound release test receipt."""

    source_revision: str
    source_tree: str
    source_clean: bool
    dirty_paths: tuple[str, ...]
    test_paths: tuple[str, ...]
    pytest_args: tuple[str, ...]
    command: tuple[str, ...]
    exit_code: int
    total: int
    failures: int
    errors: int
    skipped: int
    skipped_tests: tuple[SkippedTest, ...]
    warnings: tuple[WarningEvent, ...]
    max_skips: int
    max_warnings: int
    require_clean_source: bool
    allowed_output_paths: tuple[str, ...] = ()
    errors_detail: tuple[str, ...] = ()
    generated_at: float = 0.0
    required_output_paths: tuple[str, ...] = ()
    fresh_output_paths: tuple[str, ...] = ()
    junit_report_sha256: str = ""
    profile: str = "local"
    coverage_report: str | None = None
    coverage_report_sha256: str = ""
    coverage_line_rate_percent: float | None = None
    coverage_floor_percent: float | None = None

    @property
    def blockers(self) -> tuple[str, ...]:
        """Return every reason this receipt cannot certify a release."""
        blockers = list(self.errors_detail)
        if self.profile not in _EVIDENCE_PROFILES:
            blockers.append(f"unsupported evidence profile: {self.profile}")
        if self.profile == "release" and not self.require_clean_source:
            blockers.append("release profile must require a clean source checkout")
        if self.profile == "release" and self.max_warnings != 0:
            blockers.append("release profile must allow zero warnings")
        # Local runs may execute from a dirty checkout, but their receipts are
        # diagnostic evidence rather than certifiable release evidence.
        if not self.source_clean:
            blockers.append("source checkout is dirty")
        if self.exit_code != 0:
            blockers.append(f"pytest exited with code {self.exit_code}")
        if self.total <= 0:
            blockers.append("JUnit evidence contains no executed tests")
        if len(self.junit_report_sha256) != 64 or any(
            character not in "0123456789abcdef"
            for character in self.junit_report_sha256.lower()
        ):
            blockers.append("JUnit evidence digest is missing or malformed")
        if self.skipped != len(self.skipped_tests):
            blockers.append(
                "JUnit skipped-test count does not match recorded skipped tests"
            )
        if any(not item.reason.strip() for item in self.skipped_tests):
            blockers.append("JUnit skipped-test evidence contains an empty reason")
        if self.failures:
            blockers.append(f"JUnit evidence contains {self.failures} failed tests")
        if self.errors:
            blockers.append(f"JUnit evidence contains {self.errors} test errors")
        if any(
            value < 0
            for value in (self.total, self.failures, self.errors, self.skipped)
        ):
            blockers.append("JUnit evidence contains a negative outcome count")
        if self.failures + self.errors + self.skipped > self.total:
            blockers.append("JUnit outcome counts exceed the total test count")
        if self.skipped > self.max_skips:
            blockers.append(
                f"JUnit evidence contains {self.skipped} skipped tests; "
                f"maximum allowed is {self.max_skips}"
            )
        if self.max_skips < 0 or self.max_warnings < 0:
            blockers.append("test-evidence budgets cannot be negative")
        warning_count = len(self.warnings)
        if warning_count > self.max_warnings:
            blockers.append(
                f"pytest emitted {warning_count} warnings; "
                f"maximum allowed is {self.max_warnings}"
            )
        missing_outputs = tuple(
            path
            for path in self.required_output_paths
            if path not in self.fresh_output_paths
        )
        if missing_outputs:
            blockers.append(
                "required test outputs were not freshly produced: "
                + ", ".join(missing_outputs)
            )
        if self.profile == "release":
            if not self.coverage_report:
                blockers.append("release profile is missing a coverage report")
            if len(self.coverage_report_sha256) != 64 or any(
                character not in "0123456789abcdef"
                for character in self.coverage_report_sha256.lower()
            ):
                blockers.append("release profile is missing a coverage report digest")
            if self.coverage_floor_percent is None:
                blockers.append("release profile is missing a coverage floor")
        if self.coverage_floor_percent is not None:
            if not math.isfinite(self.coverage_floor_percent) or not (
                0 <= self.coverage_floor_percent <= 100
            ):
                blockers.append("coverage floor must be between 0 and 100 percent")
            if self.coverage_line_rate_percent is None:
                blockers.append("coverage floor has no measured coverage evidence")
            elif not math.isfinite(self.coverage_line_rate_percent) or not (
                0 <= self.coverage_line_rate_percent <= 100
            ):
                blockers.append("measured coverage must be between 0 and 100 percent")
            elif self.coverage_line_rate_percent < self.coverage_floor_percent:
                blockers.append(
                    f"coverage is {self.coverage_line_rate_percent:.2f}%; "
                    f"minimum required is {self.coverage_floor_percent:.2f}%"
                )
        return tuple(dict.fromkeys(blockers))

    @property
    def certified(self) -> bool:
        """Whether the evidence satisfies the complete release policy."""
        return not self.blockers

    def to_dict(self) -> dict[str, Any]:
        """Serialize the receipt without machine-specific checkout paths."""
        return {
            "schema_version": 2,
            "status": "pass" if self.certified else "fail",
            "certified": self.certified,
            "profile": self.profile,
            "generated_at": self.generated_at,
            "source": {
                "revision": self.source_revision,
                "tree": self.source_tree,
                "clean": self.source_clean,
                "dirty_paths": list(self.dirty_paths),
            },
            "test_selection": list(self.test_paths),
            "pytest_args": list(self.pytest_args),
            "command": list(self.command),
            "results": {
                "total": self.total,
                "failures": self.failures,
                "errors": self.errors,
                "skipped": self.skipped,
                "junit_report_sha256": self.junit_report_sha256,
            },
            "skipped_tests": [item.to_dict() for item in self.skipped_tests],
            "warnings": [item.to_dict() for item in self.warnings],
            "policy": {
                "max_skips": self.max_skips,
                "max_warnings": self.max_warnings,
                "require_clean_source": self.require_clean_source,
                "allowed_output_paths": list(self.allowed_output_paths),
                "required_output_paths": list(self.required_output_paths),
            },
            "fresh_output_paths": list(self.fresh_output_paths),
            "coverage": {
                "report": self.coverage_report,
                "sha256": self.coverage_report_sha256,
                "line_rate_percent": self.coverage_line_rate_percent,
                "floor_percent": self.coverage_floor_percent,
            },
            "blockers": list(self.blockers),
            "errors": list(self.errors_detail),
        }


def _local_name(tag: str) -> str:
    """Return an XML tag name without an optional namespace prefix."""
    return tag.rsplit("}", 1)[-1]


def _nonnegative_int(value: str | None, *, field: str) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(value)
    except ValueError as exc:
        raise EvidenceFormatError(f"JUnit {field} is not an integer") from exc
    if parsed < 0:
        raise EvidenceFormatError(f"JUnit {field} is negative")
    return parsed


def _testcase_nodeid(case: ET.Element) -> str:
    explicit = case.attrib.get("nodeid", "").strip()
    if explicit:
        return explicit
    classname = case.attrib.get("classname", "").strip()
    name = case.attrib.get("name", "").strip()
    if classname and name:
        return f"{classname}::{name}"
    return name or classname or "<unnamed-test>"


def parse_junit_xml(path: Path) -> JUnitEvidence:
    """Parse JUnit XML and preserve every skipped test reason.

    Counts are derived from individual ``testcase`` elements and cross-checked
    against leaf ``testsuite`` attributes when present.  A missing, malformed,
    or internally inconsistent report raises instead of becoming an empty
    successful receipt.
    """
    try:
        if not path.is_file():
            raise EvidenceFormatError(f"JUnit report is missing: {path}")
        raw_xml = path.read_bytes()
    except OSError as exc:
        raise EvidenceFormatError(f"JUnit report cannot be read: {exc}") from exc
    if not raw_xml:
        raise EvidenceFormatError("JUnit report is empty")
    if b"<!doctype" in raw_xml.lower() or b"<!entity" in raw_xml.lower():
        raise EvidenceFormatError("JUnit report contains unsupported DTD/entity input")
    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError as exc:
        raise EvidenceFormatError(f"JUnit report cannot be parsed: {exc}") from exc

    if _local_name(root.tag) not in {"testsuite", "testsuites"}:
        raise EvidenceFormatError("JUnit root must be testsuite or testsuites")

    suites = [
        element
        for element in root.iter()
        if _local_name(element.tag) == "testsuite"
        and not any(_local_name(child.tag) == "testsuite" for child in element)
    ]
    cases = [
        element for element in root.iter() if _local_name(element.tag) == "testcase"
    ]
    if not suites:
        raise EvidenceFormatError("JUnit report contains no testsuite")

    skipped_tests: list[SkippedTest] = []
    failure_tests: list[str] = []
    error_tests: list[str] = []
    for case in cases:
        nodeid = _testcase_nodeid(case)
        if nodeid == "<unnamed-test>":
            raise EvidenceFormatError("JUnit testcase has no identifying attributes")
        child_tags = {_local_name(child.tag) for child in case}
        outcomes = child_tags & {"failure", "error", "skipped"}
        status = case.attrib.get("status", "").strip().lower()
        if status in {"skip", "skipped"} and "skipped" not in outcomes:
            raise EvidenceFormatError(
                f"JUnit testcase status says skipped without a skipped element: {nodeid}"
            )
        if (
            status in {"fail", "failed", "failure"}
            and not {
                "failure",
                "error",
            }
            & outcomes
        ):
            raise EvidenceFormatError(
                f"JUnit testcase status says failed without a failure element: {nodeid}"
            )
        if status in {"error", "errored"} and "error" not in outcomes:
            raise EvidenceFormatError(
                f"JUnit testcase status says error without an error element: {nodeid}"
            )
        hidden_outcomes = child_tags & {"flakyFailure", "rerunFailure", "rerunError"}
        if hidden_outcomes:
            raise EvidenceFormatError(
                f"JUnit testcase has unsupported outcome elements: {nodeid}"
            )
        if len(outcomes) > 1:
            raise EvidenceFormatError(f"JUnit testcase has multiple outcomes: {nodeid}")
        if "skipped" in outcomes:
            skipped = next(
                child for child in case if _local_name(child.tag) == "skipped"
            )
            reason = skipped.attrib.get("message", "").strip()
            if not reason:
                reason = skipped.attrib.get("reason", "").strip()
            if not reason:
                reason = "".join(skipped.itertext()).strip()
            if not reason:
                raise EvidenceFormatError(
                    f"JUnit skipped testcase has no reason: {nodeid}"
                )
            skipped_tests.append(SkippedTest(nodeid=nodeid, reason=reason))
        elif "failure" in outcomes:
            failure_tests.append(nodeid)
        elif "error" in outcomes:
            error_tests.append(nodeid)

    total = len(cases)
    failures = len(failure_tests)
    errors = len(error_tests)
    skipped = len(skipped_tests)

    declared = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    declared_fields: set[str] = set()
    for suite in suites:
        for field in declared:
            parsed = _nonnegative_int(suite.attrib.get(field), field=field)
            if parsed is not None:
                declared[field] += parsed
                declared_fields.add(field)
    actual = {
        "tests": total,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
    }
    if cases:
        for field in declared_fields:
            if declared[field] != actual[field]:
                raise EvidenceFormatError(
                    f"JUnit {field} count {declared[field]} does not match "
                    f"testcase evidence {actual[field]}"
                )
    else:
        raise EvidenceFormatError("JUnit report contains no testcase evidence")

    return JUnitEvidence(
        total=total,
        failures=failures,
        errors=errors,
        skipped=skipped,
        skipped_tests=tuple(skipped_tests),
        failure_tests=tuple(failure_tests),
        error_tests=tuple(error_tests),
    )


def _coverage_count(value: str | None, *, field: str) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(value)
    except ValueError as exc:
        raise EvidenceFormatError(f"coverage {field} is not an integer") from exc
    if parsed < 0:
        raise EvidenceFormatError(f"coverage {field} is negative")
    return parsed


def _coverage_rate(value: str | None, *, field: str) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except ValueError as exc:
        raise EvidenceFormatError(f"coverage {field} is not numeric") from exc
    if not math.isfinite(parsed) or not 0 <= parsed <= 1:
        raise EvidenceFormatError(f"coverage {field} is outside the range 0..1")
    return parsed


def parse_coverage_xml(path: Path) -> CoverageEvidence:
    """Parse and validate a coverage.py-compatible Cobertura XML report."""
    try:
        if not path.is_file():
            raise EvidenceFormatError(f"coverage report is missing: {path}")
        raw_xml = path.read_bytes()
    except OSError as exc:
        raise EvidenceFormatError(f"coverage report cannot be read: {exc}") from exc
    if not raw_xml:
        raise EvidenceFormatError("coverage report is empty")
    if b"<!doctype" in raw_xml.lower() or b"<!entity" in raw_xml.lower():
        raise EvidenceFormatError(
            "coverage report contains unsupported DTD/entity input"
        )
    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError as exc:
        raise EvidenceFormatError(f"coverage report cannot be parsed: {exc}") from exc
    if _local_name(root.tag) != "coverage":
        raise EvidenceFormatError("coverage report root must be coverage")

    line_rate = _coverage_rate(root.attrib.get("line-rate"), field="line-rate")
    if line_rate is None:
        raise EvidenceFormatError("coverage report is missing line-rate")
    lines_covered = _coverage_count(
        root.attrib.get("lines-covered"), field="lines-covered"
    )
    lines_valid = _coverage_count(root.attrib.get("lines-valid"), field="lines-valid")
    if (lines_covered is None) != (lines_valid is None):
        raise EvidenceFormatError(
            "coverage report must provide both lines-covered and lines-valid"
        )
    if lines_covered is not None and lines_valid is not None:
        if lines_covered > lines_valid:
            raise EvidenceFormatError("coverage lines-covered exceeds lines-valid")
        expected = lines_covered / lines_valid if lines_valid else 0.0
        if not math.isclose(line_rate, expected, abs_tol=0.0001):
            raise EvidenceFormatError(
                "coverage line-rate does not match lines-covered/lines-valid"
            )
    _coverage_rate(root.attrib.get("branch-rate"), field="branch-rate")
    return CoverageEvidence(
        line_rate_percent=line_rate * 100,
        lines_covered=lines_covered,
        lines_valid=lines_valid,
        version=root.attrib.get("version") or None,
    )


class _WarningCollector:
    """Minimal pytest plugin collecting warning events without mocks."""

    def __init__(self) -> None:
        self.events: list[WarningEvent] = []

    def pytest_warning_recorded(
        self,
        warning_message: warnings.WarningMessage,
        when: str,
        nodeid: str,
        location: Any = None,
    ) -> None:
        del location
        category = warning_message.category
        category_name = getattr(category, "__name__", str(category))
        self.events.append(
            WarningEvent(
                message=str(warning_message.message),
                category=category_name,
                filename=str(warning_message.filename),
                lineno=int(warning_message.lineno or 0),
                nodeid=str(nodeid or ""),
                when=str(when),
            )
        )


def _git(root: Path, *args: str) -> tuple[int, str, str]:
    try:
        result = subprocess.run(  # nosec B603, B607
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, "", str(exc)
    return result.returncode, result.stdout.rstrip("\n"), result.stderr.strip()


def _status_paths(status: str) -> tuple[str, ...]:
    """Parse porcelain-v1 ``-z`` output without losing rename paths."""
    paths: list[str] = []
    records = status.split("\0")
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        path = record[3:] if len(record) >= 3 else record
        if path:
            paths.append(path)
        status_code = record[:2]
        if status_code and any(value in status_code for value in "RC"):
            if index < len(records) and records[index]:
                paths.append(records[index])
                index += 1
    return tuple(paths)


def _source_identity(
    root: Path,
) -> tuple[str, str, bool, tuple[str, ...], tuple[str, ...]]:
    errors: list[str] = []
    revision_code, revision, revision_error = _git(root, "rev-parse", "HEAD")
    tree_code, tree, tree_error = _git(root, "rev-parse", "HEAD^{tree}")
    status_code, status, status_error = _git(
        root, "status", "--porcelain=v1", "-z", "--untracked-files=all"
    )
    if revision_code != 0 or not revision:
        errors.append(
            f"source revision is unavailable: {revision_error or 'git error'}"
        )
    if tree_code != 0 or not tree:
        errors.append(f"source tree is unavailable: {tree_error or 'git error'}")
    if status_code != 0:
        errors.append(f"source status is unavailable: {status_error or 'git error'}")
    dirty_paths = _status_paths(status)
    return (
        revision,
        tree,
        not dirty_paths and status_code == 0,
        dirty_paths,
        tuple(errors),
    )


def _normalize_test_paths(
    root: Path, paths: Iterable[str | Path]
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    normalized: list[str] = []
    errors: list[str] = []
    for raw in paths:
        value = str(raw).strip()
        if not value:
            errors.append("test selection contains an empty path")
            continue
        path_part, separator, selector = value.partition("::")
        candidate = Path(path_part)
        if candidate.is_absolute() or ".." in candidate.parts:
            errors.append(f"test selection is not repository-relative: {value}")
            continue
        resolved = (root / candidate).resolve()
        try:
            relative = resolved.relative_to(root)
        except ValueError:
            errors.append(f"test selection escapes the repository: {value}")
            continue
        if not resolved.exists():
            errors.append(f"test selection does not exist: {value}")
            continue
        normalized_value = relative.as_posix()
        if separator:
            normalized_value += f"::{selector}"
        normalized.append(normalized_value)
    if not normalized:
        errors.append("test selection is empty")
    return tuple(normalized), tuple(errors)


def _normalize_output_paths(
    root: Path, paths: Iterable[str | Path]
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Normalize explicitly permitted test-report outputs."""
    normalized: list[str] = []
    errors: list[str] = []
    for raw in paths:
        value = str(raw).strip()
        candidate = Path(value)
        if not value or candidate.is_absolute() or ".." in candidate.parts:
            errors.append(f"allowed output path is not repository-relative: {value}")
            continue
        resolved = (root / candidate).resolve()
        try:
            relative = resolved.relative_to(root)
        except ValueError:
            errors.append(f"allowed output path escapes the repository: {value}")
            continue
        normalized.append(relative.as_posix())
    unique_paths = tuple(dict.fromkeys(normalized))
    for relative in unique_paths:
        code, tracked, git_error = _git(root, "ls-files", "--", relative)
        if code != 0:
            errors.append(
                f"cannot verify allowed output path {relative}: "
                f"{git_error or 'git error'}"
            )
        elif tracked.strip():
            errors.append(f"allowed output path overlaps tracked source: {relative}")
    return unique_paths, tuple(errors)


def _unsafe_pytest_arg(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith(
        (
            "--junitxml",
            "--junit-xml",
            "--override-ini",
            "-w",
            "--pythonwarnings",
            "--disable-warnings",
            "-p",
            "--plugin",
            "--ignore",
            "--deselect",
            "-k",
            "--collect-only",
            "--lf",
            "--last-failed",
            "--ff",
            "--failed-first",
            "--sw",
            "--stepwise",
            "--stepwise-skip",
            "--pyargs",
        )
    )


def _write_receipt(path: Path, evidence: ReleaseTestEvidence) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(evidence.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fresh_output_paths(
    root: Path, paths: Iterable[str], started_at_ns: int
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return required outputs modified during this invocation and blockers."""
    fresh: list[str] = []
    errors: list[str] = []
    for relative in paths:
        output = root / relative
        try:
            resolved = output.resolve()
            resolved.relative_to(root)
            stat = output.stat()
        except (OSError, ValueError) as exc:
            errors.append(f"required test output is unavailable: {relative} ({exc})")
            continue
        if not output.is_file():
            errors.append(f"required test output is not a file: {relative}")
            continue
        if stat.st_mtime_ns <= started_at_ns:
            errors.append(
                f"required test output was not refreshed during the run: {relative}"
            )
            continue
        fresh.append(relative)
    return tuple(fresh), tuple(errors)


def run_release_test_evidence(
    repo_root: str | Path = ".",
    test_paths: Iterable[str | Path] = (),
    *,
    pytest_args: Sequence[str] = (),
    receipt_path: str | Path | None = None,
    max_skips: int = 50,
    max_warnings: int = 0,
    require_clean_source: bool | None = None,
    allowed_output_paths: Iterable[str | Path] = (),
    required_output_paths: Iterable[str | Path] = (),
    profile: EvidenceProfile = "local",
    coverage_report_path: str | Path | None = None,
    coverage_floor_percent: float | None = None,
) -> ReleaseTestEvidence:
    """Run pytest and produce fail-closed, source-bound evidence.

    The function intentionally rejects caller-supplied JUnit or warning
    configuration.  It owns those inputs so a stale report or permissive
    warning filter cannot be mistaken for current release evidence.
    """
    errors: list[str] = []
    profile_value = str(profile).strip().lower()
    if profile_value not in _EVIDENCE_PROFILES:
        errors.append(f"unsupported evidence profile: {profile_value}")
    if require_clean_source is None:
        require_clean_source = profile_value == "release"
    if profile_value == "release" and not require_clean_source:
        errors.append("release profile requires a clean source checkout")
    if profile_value == "release" and max_warnings != 0:
        errors.append("release profile requires max_warnings=0")
    if profile_value == "release" and coverage_report_path is None:
        errors.append("release profile requires a coverage report path")
    if profile_value == "release" and coverage_floor_percent is None:
        errors.append("release profile requires an explicit coverage floor")
    normalized_coverage_floor: float | None = None
    if coverage_floor_percent is not None:
        try:
            normalized_coverage_floor = float(coverage_floor_percent)
        except (TypeError, ValueError):
            errors.append(f"coverage floor is not numeric: {coverage_floor_percent}")
        else:
            if not math.isfinite(normalized_coverage_floor) or not (
                0 <= normalized_coverage_floor <= 100
            ):
                errors.append("coverage floor must be between 0 and 100 percent")
    if max_skips < 0:
        errors.append("maximum skipped tests cannot be negative")
    if max_warnings < 0:
        errors.append("maximum warnings cannot be negative")

    root = Path(repo_root).resolve()
    if not root.is_dir():
        errors.append(f"repository root is not a directory: {root}")
        source_revision = ""
        source_tree = ""
        source_clean = False
        dirty_paths: tuple[str, ...] = ()
    else:
        source_revision, source_tree, source_clean, dirty_paths, source_errors = (
            _source_identity(root)
        )
        errors.extend(source_errors)

    normalized_paths: tuple[str, ...] = ()
    normalized_output_paths: tuple[str, ...] = ()
    normalized_required_output_paths: tuple[str, ...] = ()
    normalized_coverage_path: str | None = None
    required_output_values = tuple(required_output_paths)
    if coverage_report_path is not None:
        required_output_values += (coverage_report_path,)
    if root.is_dir():
        normalized_paths, path_errors = _normalize_test_paths(root, test_paths)
        errors.extend(path_errors)
        normalized_output_paths, output_errors = _normalize_output_paths(
            root, allowed_output_paths
        )
        errors.extend(output_errors)
        normalized_required_output_paths, required_output_errors = (
            _normalize_output_paths(root, required_output_values)
        )
        errors.extend(required_output_errors)
        if coverage_report_path is not None:
            coverage_paths, coverage_path_errors = _normalize_output_paths(
                root, (coverage_report_path,)
            )
            errors.extend(coverage_path_errors)
            if coverage_paths:
                normalized_coverage_path = coverage_paths[0]
        normalized_output_paths = tuple(
            dict.fromkeys((*normalized_output_paths, *normalized_required_output_paths))
        )

    normalized_args = tuple(str(value) for value in pytest_args)
    unsafe_args = [value for value in normalized_args if _unsafe_pytest_arg(value)]
    if unsafe_args:
        errors.append(
            "pytest arguments cannot override source-bound JUnit or warning policy: "
            + ", ".join(unsafe_args)
        )

    if require_clean_source and not source_clean:
        errors.append("source checkout is dirty or source status is unavailable")

    baseline_dirty_paths = set(dirty_paths)
    required_outputs_present_before_run = tuple(
        relative
        for relative in normalized_required_output_paths
        if (root / relative).exists()
    )
    if profile_value == "release" and required_outputs_present_before_run:
        errors.append(
            "release required outputs already exist before the run; refusing stale evidence: "
            + ", ".join(required_outputs_present_before_run)
        )
    exit_code = 2
    total = failures = test_errors = skipped = 0
    skipped_tests: tuple[SkippedTest, ...] = ()
    warning_events: tuple[WarningEvent, ...] = ()
    junit_report_sha256 = ""
    fresh_output_paths: tuple[str, ...] = ()
    coverage_line_rate_percent: float | None = None
    coverage_report_sha256 = ""
    command = ("python", "-m", "pytest", *normalized_args, *normalized_paths)

    if not errors:
        run_started_ns = time.time_ns()
        with tempfile.TemporaryDirectory(prefix="codomyrmex-release-evidence-") as temp:
            junit_path = Path(temp) / "junit.xml"
            final_args = [
                # Release evidence is deterministic test evidence, not a
                # benchmark run. Disabling the benchmark plugin also avoids
                # PytestBenchmarkWarning when this function is itself called
                # from an xdist worker.
                "-p",
                "no:benchmark",
                *normalized_args,
                *normalized_paths,
                f"--junitxml={junit_path}",
                # Record all unsuppressed warnings and enforce the zero-warning
                # release policy in this module instead of trusting ambient ini.
                "--override-ini=filterwarnings=default",
            ]
            command = ("python", "-m", "pytest", *final_args)
            collector = _WarningCollector()
            try:
                import pytest

                with contextlib.chdir(root):
                    exit_code = int(pytest.main(final_args, plugins=[collector]))
            except Exception as exc:  # pragma: no cover - defensive process guard
                errors.append(f"pytest invocation failed: {exc}")
                exit_code = 2
            warning_events = tuple(collector.events)
            try:
                parsed = parse_junit_xml(junit_path)
            except EvidenceFormatError as exc:
                errors.append(str(exc))
            else:
                total = parsed.total
                failures = parsed.failures
                test_errors = parsed.errors
                skipped = parsed.skipped
                skipped_tests = parsed.skipped_tests
                try:
                    junit_report_sha256 = _sha256_file(junit_path)
                except OSError as exc:
                    errors.append(f"JUnit report digest cannot be read: {exc}")
            command = tuple(
                "--junitxml=<temporary-junit.xml>"
                if value == f"--junitxml={junit_path}"
                else value
                for value in command
            )

        post_revision, post_tree, _post_clean, post_dirty_paths, post_source_errors = (
            _source_identity(root)
        )
        errors.extend(post_source_errors)
        if post_revision and source_revision and post_revision != source_revision:
            errors.append("source revision changed during the test run")
        if post_tree and source_tree and post_tree != source_tree:
            errors.append("source tree changed during the test run")
        unexpected_dirty_paths = tuple(
            path
            for path in post_dirty_paths
            if path not in normalized_output_paths and path not in baseline_dirty_paths
        )
        if unexpected_dirty_paths:
            errors.append(
                "source checkout changed during the test run: "
                + ", ".join(unexpected_dirty_paths)
            )
        source_clean = (
            source_clean and not unexpected_dirty_paths and not post_source_errors
        )
        dirty_paths = post_dirty_paths
        fresh_output_paths, output_freshness_errors = _fresh_output_paths(
            root, normalized_required_output_paths, run_started_ns
        )
        errors.extend(output_freshness_errors)
        if normalized_coverage_path is not None:
            try:
                coverage = parse_coverage_xml(root / normalized_coverage_path)
            except EvidenceFormatError as exc:
                errors.append(str(exc))
            else:
                coverage_line_rate_percent = coverage.line_rate_percent
                try:
                    coverage_report_sha256 = _sha256_file(
                        root / normalized_coverage_path
                    )
                except OSError as exc:
                    errors.append(f"coverage report digest cannot be read: {exc}")

    evidence = ReleaseTestEvidence(
        source_revision=source_revision,
        source_tree=source_tree,
        source_clean=source_clean,
        dirty_paths=dirty_paths,
        test_paths=normalized_paths,
        pytest_args=normalized_args,
        command=command,
        exit_code=exit_code,
        total=total,
        failures=failures,
        errors=test_errors,
        skipped=skipped,
        skipped_tests=skipped_tests,
        warnings=warning_events,
        max_skips=max_skips,
        max_warnings=max_warnings,
        require_clean_source=require_clean_source,
        allowed_output_paths=normalized_output_paths,
        errors_detail=tuple(errors),
        generated_at=time.time(),
        required_output_paths=normalized_required_output_paths,
        fresh_output_paths=fresh_output_paths,
        junit_report_sha256=junit_report_sha256,
        profile=profile_value,
        coverage_report=normalized_coverage_path,
        coverage_report_sha256=coverage_report_sha256,
        coverage_line_rate_percent=coverage_line_rate_percent,
        coverage_floor_percent=normalized_coverage_floor,
    )
    if receipt_path is not None:
        _write_receipt(Path(receipt_path).resolve(), evidence)
    return evidence


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run source-bound pytest evidence for release certification."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--test-path", action="append", required=True)
    parser.add_argument("--pytest-arg", action="append", default=[])
    parser.add_argument("--max-skips", type=int, default=50)
    parser.add_argument("--max-warnings", type=int, default=0)
    parser.add_argument("--allowed-output-path", action="append", default=[])
    parser.add_argument(
        "--required-output-path",
        action="append",
        default=[],
        help="repository-relative report that must be freshly produced",
    )
    parser.add_argument(
        "--profile", choices=sorted(_EVIDENCE_PROFILES), default="local"
    )
    parser.add_argument(
        "--coverage-report",
        type=Path,
        help="repository-relative coverage XML report to validate",
    )
    parser.add_argument(
        "--coverage-floor",
        type=float,
        help="minimum coverage percentage required by the selected profile",
    )
    parser.add_argument("--require-clean", action="store_true", default=None)
    parser.add_argument(
        "--allow-dirty-source",
        action="store_false",
        dest="require_clean",
        help="diagnostic-only mode; never use this for release publication",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point used by the release workflow."""
    args = _parser().parse_args(argv)
    evidence = run_release_test_evidence(
        repo_root=args.repo_root,
        test_paths=args.test_path,
        pytest_args=args.pytest_arg,
        receipt_path=args.receipt,
        max_skips=args.max_skips,
        max_warnings=args.max_warnings,
        require_clean_source=args.require_clean,
        allowed_output_paths=args.allowed_output_path,
        required_output_paths=args.required_output_path,
        profile=args.profile,
        coverage_report_path=args.coverage_report,
        coverage_floor_percent=args.coverage_floor,
    )
    print(json.dumps(evidence.to_dict(), indent=2, sort_keys=True))
    return 0 if evidence.certified else 1


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "CoverageEvidence",
    "EvidenceFormatError",
    "JUnitEvidence",
    "ReleaseTestEvidence",
    "SkippedTest",
    "WarningEvent",
    "main",
    "parse_coverage_xml",
    "parse_junit_xml",
    "run_release_test_evidence",
]
