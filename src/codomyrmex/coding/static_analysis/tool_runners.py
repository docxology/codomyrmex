"""
Tool-specific runner methods for static analysis.

Each method runs a specific external analysis tool and converts its output
into a list of AnalysisResult objects.
"""

import fnmatch
import json
import os
import re
import subprocess

from codomyrmex.coding.static_analysis.pyrefly_runner import run_pyrefly
from codomyrmex.logging_monitoring import get_logger

from .models import AnalysisResult, SeverityLevel

logger = get_logger(__name__)


_PYLINT_SEVERITY_MAP = {
    "convention": SeverityLevel.INFO,
    "refactor": SeverityLevel.WARNING,
    "warning": SeverityLevel.WARNING,
    "error": SeverityLevel.ERROR,
    "fatal": SeverityLevel.CRITICAL,
}

_BANDIT_SEVERITY_MAP = {
    "LOW": SeverityLevel.INFO,
    "MEDIUM": SeverityLevel.WARNING,
    "HIGH": SeverityLevel.ERROR,
    "CRITICAL": SeverityLevel.CRITICAL,
}

_PYREFLY_SEVERITY_MAP = {
    "error": SeverityLevel.ERROR,
    "warning": SeverityLevel.WARNING,
    "info": SeverityLevel.INFO,
}

#: Reported when the dependency scan could not be performed, so that an absent or
#: failed scanner is never mistaken for a clean one. Callers and reports can match
#: on this rule id instead of reading the message text.
SAFETY_UNAVAILABLE_RULE_ID = "SAFETY-UNAVAILABLE"

#: `severity` as it appears in a safety payload, mapped to this module's levels.
#: Anything unrecognised, including a missing value, keeps the previous default.
_SAFETY_SEVERITY_MAP = {
    "critical": SeverityLevel.CRITICAL,
    "high": SeverityLevel.ERROR,
    "medium": SeverityLevel.WARNING,
    "moderate": SeverityLevel.WARNING,
    "low": SeverityLevel.INFO,
}

#: Requirement and build files `safety check --file` can actually read. These are
#: matched as globs against the file name.
_REQUIREMENTS_PATTERNS = (
    "requirements*.txt",
    "requirements*.in",
    "Pipfile",
    "pyproject.toml",
    "setup.py",
)

#: Generated or third-party trees that never hold the project's own requirement
#: files. Walking them costs one `safety check` subprocess per match, and an
#: installed environment supplies dozens of matches on its own.
_GENERATED_DIRS = frozenset(
    {
        ".cache",
        ".eggs",
        ".git",
        ".hypothesis",
        ".mypy_cache",
        ".nox",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "env",
        "htmlcov",
        "node_modules",
        "site-packages",
        "venv",
    }
)

_ESLINT_SEVERITY_MAP = {
    1: SeverityLevel.WARNING,
    2: SeverityLevel.ERROR,
}

_SPOTBUGS_SEVERITY_MAP = {
    "LOW": SeverityLevel.INFO,
    "MEDIUM": SeverityLevel.WARNING,
    "HIGH": SeverityLevel.ERROR,
}


def safety_unavailable_result(source: str, reason: str) -> AnalysisResult:
    """Record a dependency scan that did not happen.

    The rule id, not the message, is what callers and reports match on, so an
    absent, failing or unreadable scanner is never mistaken for a clean scan.
    """
    return AnalysisResult(
        file_path=source,
        line_number=0,
        column_number=0,
        severity=SeverityLevel.WARNING,
        message=f"Dependency scan did not run: {reason}",
        rule_id=SAFETY_UNAVAILABLE_RULE_ID,
        category="security",
        suggestion="Make the safety scanner available and able to run, then re-scan",
    )


def _safety_severity(value: object) -> SeverityLevel:
    """Map a payload ``severity`` to this module's levels.

    The field is a label in some payloads and a structure in others, so anything
    unrecognised, including a missing value, keeps the historical default rather
    than discarding the whole report.
    """
    if isinstance(value, dict):
        value = value.get("severity") or value.get("source")
    label = str(value or "").rsplit(".", maxsplit=1)[-1].strip().lower()
    return _SAFETY_SEVERITY_MAP.get(label, SeverityLevel.ERROR)


def parse_safety_payload(
    payload: object, source: str
) -> tuple[list[AnalysisResult], str | None]:
    """Read a decoded ``safety check --json`` payload. Pure: no I/O, no state.

    Returns ``(findings, unavailable_reason)``. The reason is None whenever the
    payload was understood -- including when it reports no vulnerabilities -- and
    a message whenever it could not be read, so a report that cannot be parsed is
    never mistaken for a report that found nothing.

    ``safety`` writes the "1.1" format by default: an object with a
    ``vulnerabilities`` member. The older "0.5" format is a bare list and is
    still read; anything else is reported as unavailable.
    """
    if isinstance(payload, dict):
        raw = payload.get("vulnerabilities")
        if raw is None:
            members = ", ".join(sorted(payload)) or "none"
            return [], (
                "the safety JSON report has no 'vulnerabilities' member "
                f"(members: {members})"
            )
        if not isinstance(raw, list):
            return [], (
                "the safety JSON report's 'vulnerabilities' member is "
                f"{type(raw).__name__}, not a list"
            )
    elif isinstance(payload, list):
        raw = payload
    else:
        return [], (
            f"the safety JSON report is {type(payload).__name__}, which is neither "
            "the 1.1 object nor the 0.5 list"
        )

    findings = []
    for entry in raw:
        if not isinstance(entry, dict):
            return [], (
                f"a safety vulnerability entry is {type(entry).__name__}, not an object"
            )

        name = entry.get("package_name") or entry.get("package") or "unknown"
        fixed = entry.get("fixed_versions")
        if isinstance(fixed, (list, tuple, set)):
            fixed = ", ".join(sorted(str(v) for v in fixed))
        if not fixed:
            fixed = entry.get("safe_version") or "latest"

        findings.append(
            AnalysisResult(
                file_path=source,
                line_number=0,
                column_number=0,
                severity=_safety_severity(entry.get("severity")),
                message=f"Vulnerable dependency: {name}",
                rule_id="SAFETY",
                category="security",
                suggestion=f"Update to version {fixed}",
            )
        )

    return findings, None


class ToolRunner:
    """Runs external analysis tools and converts their output to AnalysisResult."""

    def __init__(self, tools_available: dict[str, bool], project_root: str) -> None:
        self.tools_available = tools_available
        self.project_root = project_root

    # ------------------------------------------------------------------ Python

    def run_pylint(self, file_path: str) -> list[AnalysisResult]:
        """Run pylint analysis on a file."""
        results = []
        try:
            cmd = ["pylint", "--output-format=json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0 and result.stdout:
                pylint_results = json.loads(result.stdout)

                for issue in pylint_results:
                    results.append(
                        AnalysisResult(
                            file_path=issue["path"],
                            line_number=issue["line"],
                            column_number=issue["column"],
                            severity=_PYLINT_SEVERITY_MAP.get(
                                issue["type"], SeverityLevel.WARNING
                            ),
                            message=issue["message"],
                            rule_id=issue["message-id"],
                            category="pylint",
                            suggestion=issue.get("suggestion"),
                            context=issue.get("context"),
                        )
                    )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error("Error running pylint on %s: %s", file_path, e)

        return results

    def run_ruff(self, file_path: str) -> list[AnalysisResult]:
        """Run the repository Ruff rules without writing a cache in the CWD."""
        results = []
        try:
            cmd = [
                "ruff",
                "check",
                "--no-cache",
                "--output-format",
                "concise",
                file_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    match = re.match(r"(.+?):(\d+):(\d+):\s+([A-Z]\d+)\s+(.+)", line)
                    if match:
                        fp, line_num, col_num, rule_id, message = match.groups()
                        severity = (
                            SeverityLevel.ERROR
                            if rule_id.startswith(("E", "F", "B", "S"))
                            else SeverityLevel.WARNING
                        )
                        results.append(
                            AnalysisResult(
                                file_path=fp,
                                line_number=int(line_num),
                                column_number=int(col_num),
                                severity=severity,
                                message=message.strip(),
                                rule_id=rule_id,
                                category="ruff",
                            )
                        )

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error("Error running ruff on %s: %s", file_path, e)

        return results

    def run_ty(self, file_path: str) -> list[AnalysisResult]:
        """Run repository type checking with Ty on a file."""
        results = []
        try:
            cmd = ["ty", "check", "--output-format", "concise", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            output = "\n".join(part for part in (result.stdout, result.stderr) if part)
            for line in output.strip().splitlines():
                match = re.match(
                    r"(.+?):(\d+):(\d+):\s+(error|warning|note):\s+(.+?)(?:\s+\[([^\]]+)\])?$",
                    line,
                )
                if match:
                    fp, line_num, col_num, level, message, error_code = match.groups()
                    severity = {
                        "error": SeverityLevel.ERROR,
                        "warning": SeverityLevel.WARNING,
                        "note": SeverityLevel.INFO,
                    }[level]
                    results.append(
                        AnalysisResult(
                            file_path=fp,
                            line_number=int(line_num),
                            column_number=int(col_num),
                            severity=severity,
                            message=message,
                            rule_id=error_code or "TY",
                            category="ty",
                        )
                    )

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error("Error running ty on %s: %s", file_path, e)

        return results

    def run_bandit(self, file_path: str) -> list[AnalysisResult]:
        """Run bandit security analysis on a file."""
        results = []
        try:
            cmd = ["bandit", "-f", "json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                bandit_results = json.loads(result.stdout)

                for issue in bandit_results.get("results", []):
                    results.append(
                        AnalysisResult(
                            file_path=issue["filename"],
                            line_number=issue["line_number"],
                            column_number=0,
                            severity=_BANDIT_SEVERITY_MAP.get(
                                issue["issue_severity"], SeverityLevel.WARNING
                            ),
                            message=issue["issue_text"],
                            rule_id=issue["test_id"],
                            category="security",
                            suggestion=issue.get("more_info"),
                        )
                    )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error("Error running bandit on %s: %s", file_path, e)

        return results

    def run_radon(self, file_path: str) -> list[AnalysisResult]:
        """Run radon complexity analysis on a file."""
        results = []
        try:
            cmd = ["radon", "cc", "-j", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                radon_results = json.loads(result.stdout)

                for file_data in radon_results.values():
                    for function_data in file_data:
                        complexity = function_data.get("complexity", 0)
                        if complexity > 10:
                            results.append(
                                AnalysisResult(
                                    file_path=file_path,
                                    line_number=function_data.get("lineno", 0),
                                    column_number=0,
                                    severity=(
                                        SeverityLevel.WARNING
                                        if complexity <= 20
                                        else SeverityLevel.ERROR
                                    ),
                                    message=f"High cyclomatic complexity: {complexity}",
                                    rule_id="RADON_CC",
                                    category="complexity",
                                    suggestion=f"Consider refactoring to reduce complexity (current: {complexity})",
                                )
                            )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error("Error running radon on %s: %s", file_path, e)

        return results

    def run_vulture(self, file_path: str) -> list[AnalysisResult]:
        """Run vulture dead code analysis on a file."""
        results = []
        try:
            cmd = ["vulture", "--min-confidence", "60", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if ":" in line:
                        parts = line.split(":", 2)
                        if len(parts) >= 3:
                            fp, line_num, message = parts

                            try:
                                ln = int(line_num)
                            except ValueError:
                                logger.debug(
                                    "vulture: could not parse line from: %r", line
                                )
                                continue

                            results.append(
                                AnalysisResult(
                                    file_path=fp,
                                    line_number=ln,
                                    column_number=0,
                                    severity=SeverityLevel.WARNING,
                                    message=message.strip(),
                                    rule_id="VULTURE",
                                    category="quality",
                                    suggestion="Consider removing unused code or adding tests",
                                )
                            )

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error("Error running vulture on %s: %s", file_path, e)

        return results

    def run_safety(self, file_path: str) -> list[AnalysisResult]:
        """Run safety dependency analysis.

        An unavailable, failing or unreadable scanner yields a typed
        `SAFETY-UNAVAILABLE` result rather than an empty list, so a dependency
        scan that did not happen can never read as a scan that found nothing.
        """
        if not self.tools_available.get("safety", False):
            return [
                safety_unavailable_result(file_path, "the safety tool is not available")
            ]

        try:
            req_files = self._find_requirements_files()
        except OSError as e:
            logger.error("Error locating requirements files for safety: %s", e)
            return [
                safety_unavailable_result(
                    file_path, f"requirements files could not be located: {e}"
                )
            ]

        if not req_files:
            return [
                safety_unavailable_result(
                    file_path, "no requirements file was found to scan"
                )
            ]

        results: list[AnalysisResult] = []
        try:
            for req_file in req_files:
                cmd = ["safety", "check", "--json", "--file", req_file]
                try:
                    completed = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=30
                    )
                except (
                    subprocess.TimeoutExpired,
                    OSError,
                    subprocess.SubprocessError,
                ) as e:
                    logger.error("Error running safety on %s: %s", req_file, e)
                    results.append(
                        safety_unavailable_result(
                            req_file, f"the scanner failed to run: {e}"
                        )
                    )
                    continue

                if not completed.stdout.strip():
                    detail = (completed.stderr or "").strip().splitlines()
                    reason = (
                        detail[-1] if detail else f"exit status {completed.returncode}"
                    )
                    logger.error(
                        "safety produced no report for %s: %s", req_file, reason
                    )
                    results.append(
                        safety_unavailable_result(
                            req_file, f"the scanner produced no report ({reason})"
                        )
                    )
                    continue

                try:
                    payload = json.loads(completed.stdout)
                except json.JSONDecodeError as e:
                    logger.error(
                        "safety returned unparseable JSON for %s: %s", req_file, e
                    )
                    results.append(
                        safety_unavailable_result(
                            req_file, "the scanner returned unparseable JSON"
                        )
                    )
                    continue

                findings, reason = parse_safety_payload(payload, req_file)
                if reason is not None:
                    logger.error(
                        "safety report for %s could not be read: %s", req_file, reason
                    )
                    results.append(safety_unavailable_result(req_file, reason))
                    continue

                results.extend(findings)

        # Backstop: anything unexpected still becomes a result, never silence.
        except Exception as e:
            logger.error("Error running safety: %s", e)
            results.append(
                safety_unavailable_result(
                    file_path, f"the scan raised {type(e).__name__}: {e}"
                )
            )

        return results

    def run_pyrefly(self, file_path: str) -> list[AnalysisResult]:
        """Run Pyrefly type checking on a file."""
        results = []
        try:
            pyrefly_result = run_pyrefly(file_path)

            if pyrefly_result.success and pyrefly_result.issues:
                for issue in pyrefly_result.issues:
                    results.append(
                        AnalysisResult(
                            file_path=issue.file_path or file_path,
                            line_number=issue.line,
                            column_number=issue.column,
                            severity=_PYREFLY_SEVERITY_MAP.get(
                                issue.severity, SeverityLevel.ERROR
                            ),
                            message=issue.message,
                            rule_id=issue.rule_id or "PYREFLY_ERROR",
                            category="type_checking",
                        )
                    )

            if pyrefly_result.error_message:
                logger.warning(
                    "Pyrefly reported error for %s: %s",
                    file_path,
                    pyrefly_result.error_message,
                )

        except (
            ImportError,
            subprocess.SubprocessError,
            FileNotFoundError,
            Exception,
        ) as e:
            logger.error("Error running Pyrefly on %s: %s", file_path, e)

        return results

    def _find_requirements_files(self) -> list[str]:
        """Find the project's own requirement and build files.

        ``run_safety`` runs one ``safety check --file`` subprocess per file this
        returns, so the walk stays out of generated and third-party trees and
        matches real file names: a file that merely *starts with*
        ``requirements`` (``requirements.py``, a ``.pyc``) is not a requirement
        file.
        """
        req_files = []
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [
                d
                for d in dirs
                if d not in _GENERATED_DIRS and not d.endswith(".egg-info")
            ]
            for file in files:
                if any(fnmatch.fnmatch(file, p) for p in _REQUIREMENTS_PATTERNS):
                    req_files.append(os.path.join(root, file))

        return req_files

    # --------------------------------------------------------------- JavaScript

    def run_eslint(self, file_path: str) -> list[AnalysisResult]:
        """Run ESLint analysis on a JavaScript/TypeScript file."""
        results = []
        try:
            cmd = ["eslint", "--format=json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                eslint_results = json.loads(result.stdout)

                for file_data in eslint_results:
                    for message in file_data.get("messages", []):
                        results.append(
                            AnalysisResult(
                                file_path=file_data["filePath"],
                                line_number=message["line"],
                                column_number=message["column"],
                                severity=_ESLINT_SEVERITY_MAP.get(
                                    message["severity"], SeverityLevel.WARNING
                                ),
                                message=message["message"],
                                rule_id=message["ruleId"],
                                category="eslint",
                                suggestion=message.get("fix"),
                            )
                        )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error("Error running eslint on %s: %s", file_path, e)

        return results

    def run_typescript_compiler(self, file_path: str) -> list[AnalysisResult]:
        """Run TypeScript compiler analysis."""
        results = []
        try:
            cmd = ["tsc", "--noEmit", "--pretty", "false", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stderr:
                for line in result.stderr.strip().split("\n"):
                    if ":" in line and "error" in line:
                        match = re.match(
                            r"([^:]+):(\d+):(\d+) - error TS(\d+): (.+)", line
                        )
                        if match:
                            fp, line_num, col_num, error_code, message = match.groups()

                            results.append(
                                AnalysisResult(
                                    file_path=fp,
                                    line_number=int(line_num),
                                    column_number=int(col_num),
                                    severity=SeverityLevel.ERROR,
                                    message=message,
                                    rule_id=f"TS{error_code}",
                                    category="typescript",
                                )
                            )

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error("Error running TypeScript compiler on %s: %s", file_path, e)

        return results

    # -------------------------------------------------------------------- Java

    def run_spotbugs(self, file_path: str) -> list[AnalysisResult]:
        """Run SpotBugs analysis on a Java file."""
        results = []
        try:
            cmd = ["spotbugs", "-textui", "-output", "json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                spotbugs_results = json.loads(result.stdout)

                for bug in spotbugs_results.get("bugs", []):
                    results.append(
                        AnalysisResult(
                            file_path=bug["file"],
                            line_number=bug["line"],
                            column_number=0,
                            severity=_SPOTBUGS_SEVERITY_MAP.get(
                                bug["priority"], SeverityLevel.WARNING
                            ),
                            message=bug["message"],
                            rule_id=bug["type"],
                            category="spotbugs",
                            suggestion=bug.get("suggestion"),
                        )
                    )

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error("Error running spotbugs on %s: %s", file_path, e)

        return results
