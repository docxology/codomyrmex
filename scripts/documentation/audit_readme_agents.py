#!/usr/bin/env python3
"""Audit first-party README.md and AGENTS.md contracts without rewriting them.

The audit complements presence, link, and structure checks by validating the
reader-facing command paths and local skill references that ordinary Markdown
link checkers cannot see. Relative links beneath registered submodule paths are
treated as externally owned when the submodule is not initialized. The audit
also inventories generated-boilerplate debt without making that legacy debt a
release-blocking error.

First-party scope follows ``scripts/rasp_gap_report.py``. The repository root
is included explicitly. Under ``tests/``, only directories that already carry
one member of the README/AGENTS pair are governed; ordinary test-leaf
directories are not required to add documentation.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[2]
_RASP_SPEC = importlib.util.spec_from_file_location(
    "_codomyrmex_rasp_gap_report",
    SCRIPT_REPO_ROOT / "scripts" / "rasp_gap_report.py",
)
if _RASP_SPEC is None or _RASP_SPEC.loader is None:
    raise RuntimeError("Could not load scripts/rasp_gap_report.py")
_RASP = importlib.util.module_from_spec(_RASP_SPEC)
_RASP_SPEC.loader.exec_module(_RASP)
ROOTS = _RASP.ROOTS
iter_dirs_under = _RASP.iter_dirs_under
should_skip_dir = _RASP.should_skip_dir


PAIR_NAMES = ("README.md", "AGENTS.md")
PYTHON_COMMAND_RE = re.compile(
    r"(?:(?:uv run(?: --locked)? )?python(?:3)?"
    r"(?: -m [\w.]+)?\s+)([A-Za-z0-9_./-]+\.py)"
)
LOCAL_SKILL_RE = re.compile(r"(?P<path>\.claude/skills/[A-Za-z0-9_./-]+/SKILL\.md)")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
SUBMODULE_PATH_RE = re.compile(
    r"^\s*path\s*=\s*(?P<path>[^\r\n]+?)\s*$",
    re.MULTILINE,
)
VERSION_RE = re.compile(r"\*\*Version\*\*:\s*v(?P<version>[0-9]+\.[0-9]+\.[0-9]+)")
PLACEHOLDER_SCRIPT_NAMES = {
    "custom_validation_script.py",
    "my_script.py",
    "script.py",
    "your_script.py",
}
GENERIC_PATTERNS = (
    re.compile(
        r"Module implementation, resources, and local coordination",
        re.IGNORECASE,
    ),
    re.compile(r"Inherits dependencies from the parent module", re.IGNORECASE),
    re.compile(
        r"(?:Project file|Directory containing .* components)",
        re.IGNORECASE,
    ),
)


@dataclass(frozen=True)
class Finding:
    """One portable README/AGENTS audit finding."""

    severity: str
    code: str
    file: str
    line: int
    message: str


def _relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _first_party_directories(repo_root: Path) -> list[Path]:
    """Return governed directories, including root and documented test leaves."""
    directories: set[Path] = {repo_root.resolve()}
    for relative_root in ROOTS:
        base = repo_root / relative_root
        directories.update(iter_dirs_under(repo_root, base))

    tests_root = repo_root / "tests"
    if tests_root.is_dir():
        directories.add(tests_root.resolve())
        for path in tests_root.rglob("*"):
            if not path.is_dir() or should_skip_dir(path, repo_root):
                continue
            if any((path / name).is_file() for name in PAIR_NAMES):
                directories.add(path.resolve())
    return sorted(directories)


def _resolve_command_path(document: Path, target: str, repo_root: Path) -> Path | None:
    """Resolve a documented Python script against plausible working directories."""
    if (
        target.startswith(("/", "SKILL_DIR/"))
        or "$" in target
        or "<" in target
        or Path(target).name in PLACEHOLDER_SCRIPT_NAMES
    ):
        return document

    candidates = [repo_root / target]
    current = document.parent.resolve()
    root = repo_root.resolve()
    while current == root or root in current.parents:
        candidates.append(current / target)
        if current == root:
            break
        current = current.parent
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def _submodule_paths(repo_root: Path) -> tuple[Path, ...]:
    """Return registered submodule paths that are not initialized locally."""
    gitmodules = repo_root / ".gitmodules"
    if not gitmodules.is_file():
        return ()
    text = gitmodules.read_text(encoding="utf-8", errors="replace")
    paths = []
    for match in SUBMODULE_PATH_RE.finditer(text):
        submodule_path = (repo_root / match.group("path").strip()).resolve()
        if not (submodule_path / ".git").exists():
            paths.append(submodule_path)
    return tuple(paths)


def _markdown_link_target_exists(
    document: Path,
    raw_target: str,
    submodule_paths: tuple[Path, ...],
) -> bool:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith(
        ("#", "http://", "https://", "mailto:", "data:")
    ):
        return True
    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return True
    resolved_target = (document.parent / target).resolve()
    if resolved_target.exists():
        return True
    return any(
        resolved_target == submodule_path or submodule_path in resolved_target.parents
        for submodule_path in submodule_paths
    )


def _file_findings(
    path: Path,
    repo_root: Path,
    submodule_paths: tuple[Path, ...],
) -> list[Finding]:
    """Validate one README/AGENTS file."""
    relative = _relative(path, repo_root)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeError as exc:
        return [
            Finding("error", "invalid_utf8", relative, 1, f"UTF-8 decode failed: {exc}")
        ]

    findings: list[Finding] = []
    lines = text.splitlines()
    if not any(line.strip() for line in lines):
        findings.append(Finding("error", "empty_file", relative, 1, "File is empty"))
    elif not any(line.startswith("# ") for line in lines[:80]):
        findings.append(
            Finding(
                "error",
                "missing_h1",
                relative,
                1,
                "File must contain an H1 within its first 80 lines",
            )
        )

    for line_number, line in enumerate(lines, 1):
        for match in PYTHON_COMMAND_RE.finditer(line):
            target = match.group(1).rstrip("`),;")
            if _resolve_command_path(path, target, repo_root) is None:
                findings.append(
                    Finding(
                        "error",
                        "missing_python_command",
                        relative,
                        line_number,
                        f"Documented Python entry point does not exist: {target}",
                    )
                )
        for match in LOCAL_SKILL_RE.finditer(line):
            target = repo_root / match.group("path")
            if not target.is_file():
                findings.append(
                    Finding(
                        "error",
                        "missing_local_skill",
                        relative,
                        line_number,
                        f"Referenced repository skill does not exist: {match.group('path')}",
                    )
                )
        for match in MARKDOWN_LINK_RE.finditer(line):
            target = match.group(1)
            if not _markdown_link_target_exists(path, target, submodule_paths):
                findings.append(
                    Finding(
                        "error",
                        "broken_markdown_link",
                        relative,
                        line_number,
                        f"Relative Markdown target does not exist: {target}",
                    )
                )

    if re.search(r"from codomyrmex\.[\w.]+ import \*", text):
        findings.append(
            Finding(
                "warning",
                "wildcard_import_example",
                relative,
                1,
                "Example uses a wildcard import instead of explicit public exports",
            )
        )
    if re.search(r"\b[A-Z][A-Za-z ]+\.\.", text):
        findings.append(
            Finding(
                "warning",
                "double_terminal_period",
                relative,
                1,
                "Generated prose contains a duplicated terminal period",
            )
        )
    return findings


def audit_repository(repo_root: Path) -> dict[str, Any]:
    """Audit the governed README/AGENTS surface and return a portable result."""
    repo_root = repo_root.resolve()
    directories = _first_party_directories(repo_root)
    findings: list[Finding] = []
    files: list[Path] = []
    metrics: Counter[str] = Counter()
    submodule_paths = _submodule_paths(repo_root)

    for directory in directories:
        present = {name: (directory / name).is_file() for name in PAIR_NAMES}
        if any(present.values()) and not all(present.values()):
            missing = next(name for name, exists in present.items() if not exists)
            findings.append(
                Finding(
                    "error",
                    "missing_pair_member",
                    _relative(directory, repo_root),
                    1,
                    f"Directory is missing {missing}",
                )
            )
        for name, exists in present.items():
            if exists:
                files.append(directory / name)

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        findings.extend(_file_findings(path, repo_root, submodule_paths))
        metrics["readme_files" if path.name == "README.md" else "agents_files"] += 1
        metrics["curated_files"] += int(": curated -->" in text[:800])
        metrics["generated_files"] += int(": generated -->" in text[:800])
        metrics["thin_files"] += int(len(text.splitlines()) < 15)
        metrics["generic_boilerplate_files"] += int(
            any(pattern.search(text) for pattern in GENERIC_PATTERNS)
        )
        version = VERSION_RE.search(text)
        metrics["legacy_v0_1_0_labels"] += int(
            bool(version and version.group("version") == "0.1.0")
        )

    findings.sort(key=lambda item: (item.severity, item.file, item.line, item.code))
    counts = Counter(item.severity for item in findings)
    return {
        "schema_version": "1",
        "scope": {
            "directory_count": len(directories),
            "file_count": len(files),
            "roots": [".", *ROOTS, "tests (documented directories only)"],
            "excluded_trees": "See scripts/rasp_gap_report.py",
        },
        "metrics": dict(sorted(metrics.items())),
        "finding_counts": {
            "error": counts["error"],
            "warning": counts["warning"],
            "total": len(findings),
        },
        "findings": [asdict(item) for item in findings],
    }


def _markdown_report(result: dict[str, Any]) -> str:
    counts = result["finding_counts"]
    metrics = result["metrics"]
    scope = result["scope"]
    lines = [
        "# README / AGENTS audit",
        "",
        "Read-only audit of first-party folder documentation contracts.",
        "",
        "## Summary",
        "",
        f"- Governed directories: **{scope['directory_count']}**",
        f"- Files checked: **{scope['file_count']}**",
        f"- Errors: **{counts['error']}**",
        f"- Warnings: **{counts['warning']}**",
        f"- Generic-boilerplate inventory: **{metrics.get('generic_boilerplate_files', 0)}** files",
        f"- Legacy `v0.1.0` labels: **{metrics.get('legacy_v0_1_0_labels', 0)}** files",
        f"- Thin files under 15 lines: **{metrics.get('thin_files', 0)}**",
        "",
        "Legacy and generic-copy metrics are inventory signals, not automatic "
        "evidence that a leaf signpost is inaccurate.",
        "",
        "## Findings",
        "",
    ]
    if not result["findings"]:
        lines.append("No blocking or warning findings.")
    else:
        lines.extend(
            [
                "| Severity | Code | File | Line | Message |",
                "| :--- | :--- | :--- | ---: | :--- |",
            ]
        )
        for finding in result["findings"]:
            message = finding["message"].replace("|", "\\|")
            lines.append(
                f"| {finding['severity']} | `{finding['code']}` | "
                f"`{finding['file']}` | {finding['line']} | {message} |"
            )
    lines.append("")
    return "\n".join(lines)


def write_reports(
    result: dict[str, Any],
    *,
    json_path: Path | None,
    markdown_path: Path | None,
) -> None:
    """Write requested audit receipts."""
    if json_path is not None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if markdown_path is not None:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(_markdown_report(result), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit README.md and AGENTS.md contracts without rewriting them"
    )
    parser.add_argument("--repo-root", type=Path, default=SCRIPT_REPO_ROOT)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("output/readme_agents_audit.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("output/readme_agents_audit.md"),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when blocking errors are found",
    )
    return parser


def _resolve_output(path: Path, repo_root: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    result = audit_repository(repo_root)
    write_reports(
        result,
        json_path=_resolve_output(args.json_output, repo_root),
        markdown_path=_resolve_output(args.markdown_output, repo_root),
    )
    counts = result["finding_counts"]
    print(
        "README/AGENTS audit: "
        f"{result['scope']['directory_count']} directories, "
        f"{result['scope']['file_count']} files, "
        f"{counts['error']} errors, {counts['warning']} warnings"
    )
    return 1 if args.strict and counts["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
