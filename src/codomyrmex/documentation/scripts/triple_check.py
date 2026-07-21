#!/usr/bin/env python3
"""Comprehensive triple-check of all SPEC, AGENTS, and README files."""

import argparse
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

DocIssue = dict[str, Any]


class ResultCategories(TypedDict):
    """Grouped documentation findings and aggregate counts."""

    placeholders: list[DocIssue]
    broken_links: list[DocIssue]
    completeness: list[DocIssue]
    total_placeholders: int
    total_broken_links: int
    total_completeness: int


# Placeholder patterns (using raw strings for proper regex escaping). The marker
# patterns intentionally require task-style syntax so prose such as "TODO
# queues" and API names such as "todo.py" do not inflate documentation debt.
PLACEHOLDER_PATTERNS = [
    (r"\[Architecture description[^\]]*\]", "Architecture description placeholder"),
    (r"\[Functional requirements[^\]]*\]", "Functional requirements placeholder"),
    (r"\[Testing, documentation[^\]]*\]", "Requirements placeholder"),
    (r"\[APIs, data structures[^\]]*\]", "Interface placeholder"),
    (r"\[How to implement[^\]]*\]", "Implementation placeholder"),
    (r"\[Brief description[^\]]*\]", "Brief description placeholder"),
    (r"\[Module Name\]", "Module name placeholder"),
    (r"\[MainClass\]", "Main class placeholder"),
    (r"\[module_name\]", "Module name variable placeholder"),
    (
        r"(?m)(?:^|\n)[ \t]*(?:[-*+]\s*)?(?:#{1,6}\s*)?(?:<!--\s*)?"
        r"(?:\*{0,2})TODO(?:\*{0,2})\b\s*[:\[(]",
        "TODO marker",
    ),
    (
        r"(?m)(?:^|\n)[ \t]*(?:[-*+]\s*)?(?:#{1,6}\s*)?(?:<!--\s*)?"
        r"(?:\*{0,2})FIXME(?:\*{0,2})\b\s*[:\[(]",
        "FIXME marker",
    ),
    (
        r"(?m)(?:^|\n)[ \t]*(?:[-*+]\s*)?(?:#{1,6}\s*)?(?:<!--\s*)?"
        r"XXX\b\s*[:\[(]",
        "XXX marker",
    ),
    (r"\[TBD\]|\(\s*TBD\b[^)]*\)|\bTBD\b\s*[:\[(]", "TBD marker"),
    (
        r"\[placeholder\]|\bplaceholder\s*[:=]|\(\s*placeholder\b[^)]*\)",
        "PLACEHOLDER marker",
    ),
    (r"to be completed", "To be completed"),
    (r"coming soon", "Coming soon"),
    (r"needs filling", "Needs filling"),
    (r"needs specific content", "Needs specific content"),
    (r"Contains components for the src system", "Generic placeholder"),
    (r"Documentation files and guides\.$", "Generic docs placeholder"),
    (r"Test files and validation suites\.$", "Generic test placeholder"),
]


def _mask_markdown_code(content: str) -> str:
    """Blank markdown code spans/blocks while preserving positions."""

    def blank(match: re.Match[str]) -> str:
        return "".join("\n" if char == "\n" else " " for char in match.group(0))

    masked = re.sub(r"(?ms)^(```|~~~)[^\n]*\n.*?^\1\s*$", blank, content)
    return re.sub(r"`[^`\n]+`", blank, masked)


def find_placeholders(content: str, file_path: Path) -> list[DocIssue]:
    """Find placeholder content in file."""
    issues = []
    searchable_content = _mask_markdown_code(content)
    for pattern, description in PLACEHOLDER_PATTERNS:
        matches = re.finditer(pattern, searchable_content, re.IGNORECASE)
        for match in matches:
            # Get context
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end].replace("\n", " ")

            issues.append(
                {
                    "pattern": pattern,
                    "description": description,
                    "match": match.group(0),
                    "position": match.start(),
                    "line": content[: match.start()].count("\n") + 1,
                    "context": context,
                }
            )
    return issues


def verify_relative_path(
    link_url: str, from_file: Path, base_path: Path
) -> tuple[bool, str, Path | None]:
    """Verify if a relative path is correct."""
    if link_url.startswith(("http://", "https://", "mailto:", "#")):
        return (True, "", None)  # External links and anchors are OK

    # Remove anchor
    clean_url = link_url.split("#", maxsplit=1)[0]
    if not clean_url:
        return (True, "", None)

    # Resolve path
    clean_url = clean_url.removeprefix("./")

    if clean_url.startswith("../"):
        levels_up = clean_url.count("../")
        base_dir = from_file.parent
        for _ in range(levels_up):
            if base_dir == base_dir.parent:  # Reached root
                return (False, "Too many ../ levels", None)
            base_dir = base_dir.parent
        while clean_url.startswith("../"):
            clean_url = clean_url.removeprefix("../")
        resolved = base_dir / clean_url
    elif clean_url.startswith("/"):
        resolved = base_path / clean_url.lstrip("/")
    else:
        resolved = from_file.parent / clean_url

    # Normalize path
    try:
        resolved = resolved.resolve()
        exists = resolved.exists()
        if not exists:
            return (False, f"Path does not exist: {resolved}", resolved)
        return (True, "", resolved)
    except Exception as e:
        return (False, f"Error resolving path: {e}", None)


def check_file_completeness(content: str, file_path: Path) -> list[str]:
    """Check for the small, universal documentation contract.

    Structural requirements for ``AGENTS.md`` are owned by
    ``validate_agents_structure.py`` and link requirements are owned by the
    comprehensive link validator.  This legacy checker should not reject
    concise, hand-maintained signposts merely because they omit metadata or a
    sibling document that does not exist.  Keep this check focused on content
    that is universally actionable: a heading and meaningful prose.
    """
    del file_path  # The current contract is intentionally path-independent.
    issues: list[str] = []
    headings = [line for line in content.splitlines() if line.lstrip().startswith("#")]
    prose = [
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    if not headings:
        issues.append("Missing document heading")
    if len(" ".join(prose).split()) < 10:
        issues.append("File appears to have minimal content")
    return issues


def analyze_file(file_path: Path, base_path: Path) -> DocIssue | None:
    """Comprehensively analyze a documentation file."""
    if not file_path.exists():
        return {
            "path": str(file_path.relative_to(base_path)),
            "error": "File does not exist",
        }

    try:
        content = file_path.read_text(encoding="utf-8")
        rel_path = str(file_path.relative_to(base_path))

        result = {
            "path": rel_path,
            "placeholders": find_placeholders(content, file_path),
            "broken_links": [],
            "completeness_issues": check_file_completeness(content, file_path),
            "total_issues": 0,
        }

        # Check all links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        matches = re.finditer(link_pattern, content)

        for match in matches:
            link_text = match.group(1)
            link_url = match.group(2)

            # Skip template placeholders in code blocks
            if "[" in link_text and "]" in link_text and link_text.startswith("["):
                # Check if it's in a code block
                start_pos = match.start()
                # Look backwards for code block markers
                before = content[max(0, start_pos - 100) : start_pos]
                if "```" in before:
                    # Count code block markers
                    code_blocks = before.count("```")
                    if code_blocks % 2 == 1:  # Inside code block
                        continue

            is_valid, error, _resolved = verify_relative_path(
                link_url, file_path, base_path
            )
            if not is_valid:
                result["broken_links"].append(
                    {
                        "text": link_text,
                        "url": link_url,
                        "error": error,
                        "line": content[: match.start()].count("\n") + 1,
                    }
                )

        result["total_issues"] = (
            len(result["placeholders"])
            + len(result["broken_links"])
            + len(result["completeness_issues"])
        )

        return result if result["total_issues"] > 0 else None

    except Exception as e:
        return {"path": str(file_path.relative_to(base_path)), "error": str(e)}


_SKIP_DIRS = frozenset(
    {
        "__pycache__",
        ".benchmarks",
        ".cache",
        ".codomyrmex",
        ".cursor",
        ".docusaurus",
        "node_modules",
        "output",
        "venv",
        ".venv",
        ".git",
        ".gitnexus",
        "@output",
    }
)
_DOC_FILENAMES = ("README.md", "AGENTS.md", "SPEC.md")


def _load_gitmodule_paths(repo_root: Path) -> set[str]:
    """Return submodule paths listed in .gitmodules."""

    gitmodules = repo_root / ".gitmodules"
    if not gitmodules.is_file():
        return set()
    paths: set[str] = set()
    for line in gitmodules.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("path ="):
            paths.add(stripped.split("=", maxsplit=1)[1].strip())
    return paths


def _collect_doc_files(base_path: Path) -> list[Path]:
    """Walk *base_path* and return all SPEC/AGENTS/README file paths."""
    doc_files: list[Path] = []
    if not base_path.is_dir():
        return doc_files
    submodule_paths = _load_gitmodule_paths(base_path.resolve())
    generated_prefixes = {
        ("docs", "manuscript"),
        ("docs", "agents", "open_gauss"),
        ("src", "codomyrmex", "documentation", "docs"),
        ("src", "codomyrmex", "agents", "open_gauss"),
        ("src", "codomyrmex", "skills", "skills", "upstream"),
    }
    for root, dirs, _files in os.walk(base_path):
        root_path = Path(root).resolve()
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in _SKIP_DIRS]
        rel_root = root_path.relative_to(base_path).parts
        dirs[:] = [
            d
            for d in dirs
            if (*rel_root, d) not in generated_prefixes
            and not any(
                (*rel_root, d)[: len(prefix)] == prefix for prefix in generated_prefixes
            )
        ]
        if submodule_paths:
            dirs[:] = [
                d
                for d in dirs
                if (root_path / d).relative_to(base_path).as_posix()
                not in submodule_paths
            ]
        for name in _DOC_FILENAMES:
            if rel_root and rel_root[0] == "tests" and len(rel_root) > 1:
                continue
            fp = root_path / name
            if fp.exists():
                doc_files.append(fp)
    return doc_files


def _categorize_results(results: list[DocIssue]) -> ResultCategories:
    """Group analysis results by issue type and compute totals."""
    return {
        "placeholders": [r for r in results if r.get("placeholders")],
        "broken_links": [r for r in results if r.get("broken_links")],
        "completeness": [r for r in results if r.get("completeness_issues")],
        "total_placeholders": sum(len(r.get("placeholders", [])) for r in results),
        "total_broken_links": sum(len(r.get("broken_links", [])) for r in results),
        "total_completeness": sum(
            len(r.get("completeness_issues", [])) for r in results
        ),
    }


def _print_console_summary(
    doc_count: int, results: list[DocIssue], cats: ResultCategories
) -> None:
    """Print a concise summary of triple-check results to stdout."""
    print("\n=== TRIPLE-CHECK SUMMARY ===")
    print(f"Total files checked: {doc_count}")
    print(f"Files with issues: {len(results)}")
    print(f"Total placeholders: {cats['total_placeholders']}")
    print(f"Total broken links: {cats['total_broken_links']}")
    print(f"Total completeness issues: {cats['total_completeness']}")

    if cats["placeholders"]:
        print(f"\n=== FILES WITH PLACEHOLDERS ({len(cats['placeholders'])}) ===")
        for result in sorted(
            cats["placeholders"],
            key=lambda x: len(x.get("placeholders", [])),
            reverse=True,
        )[:10]:
            print(f"\n{result['path']}: {len(result['placeholders'])} placeholder(s)")
            for ph in result["placeholders"][:3]:
                print(f"  Line {ph['line']}: {ph['description']} - {ph['match'][:50]}")

    if cats["broken_links"]:
        print(f"\n=== FILES WITH BROKEN LINKS ({len(cats['broken_links'])}) ===")
        for result in sorted(
            cats["broken_links"],
            key=lambda x: len(x.get("broken_links", [])),
            reverse=True,
        )[:10]:
            print(f"\n{result['path']}: {len(result['broken_links'])} broken link(s)")
            for lk in result["broken_links"][:3]:
                print(
                    f"  Line {lk['line']}: [{lk['text']}]({lk['url']}) - {lk['error']}"
                )

    if cats["completeness"]:
        print(f"\n=== FILES WITH COMPLETENESS ISSUES ({len(cats['completeness'])}) ===")
        for result in sorted(
            cats["completeness"],
            key=lambda x: len(x.get("completeness_issues", [])),
            reverse=True,
        )[:10]:
            print(f"\n{result['path']}:")
            for issue in result["completeness_issues"]:
                print(f"  - {issue}")


def _write_report(
    report_path: Path,
    doc_count: int,
    results: list[DocIssue],
    cats: ResultCategories,
) -> None:
    """Write a detailed markdown report to *report_path*."""
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = ["# Documentation Triple-Check Report\n\n"]
    report.append(f"**Generated**: {datetime.now(UTC).isoformat()}\n\n")
    report.append("## Summary\n\n")
    report.append(f"- **Total Files Checked**: {doc_count}\n")
    report.append(f"- **Files with Issues**: {len(results)}\n")
    report.append(f"- **Total Placeholders**: {cats['total_placeholders']}\n")
    report.append(f"- **Total Broken Links**: {cats['total_broken_links']}\n")
    report.append(f"- **Total Completeness Issues**: {cats['total_completeness']}\n\n")

    if cats["placeholders"]:
        report.append("## Placeholders\n\n")
        for result in sorted(
            cats["placeholders"],
            key=lambda x: len(x.get("placeholders", [])),
            reverse=True,
        ):
            report.append(f"### {result['path']}\n\n")
            for ph in result["placeholders"]:
                report.append(f"- **Line {ph['line']}**: {ph['description']}\n")
                report.append(f"  - Match: `{ph['match']}`\n")
                report.append(f"  - Context: `{ph['context'][:100]}...`\n\n")

    if cats["broken_links"]:
        report.append("## Broken Links\n\n")
        for result in sorted(
            cats["broken_links"],
            key=lambda x: len(x.get("broken_links", [])),
            reverse=True,
        ):
            report.append(f"### {result['path']}\n\n")
            for lk in result["broken_links"]:
                report.append(
                    f"- **Line {lk['line']}**: `[{lk['text']}]({lk['url']})`\n"
                )
                report.append(f"  - Error: {lk['error']}\n\n")

    if cats["completeness"]:
        report.append("## Completeness Issues\n\n")
        for result in sorted(
            cats["completeness"],
            key=lambda x: len(x.get("completeness_issues", [])),
            reverse=True,
        ):
            report.append(f"### {result['path']}\n\n")
            for issue in result["completeness_issues"]:
                report.append(f"- {issue}\n")
            report.append("\n")

    report_path.write_text("".join(report), encoding="utf-8")
    print(f"\nDetailed report: {report_path}")


def main(argv: list[str] | None = None) -> int:
    """Run comprehensive triple-check."""
    parser = argparse.ArgumentParser(
        description="Triple-check README.md, AGENTS.md, and SPEC.md files."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to scan. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=Path("output/triple_check_report.md"),
        help="Report path. Relative paths are resolved from --repo-root.",
    )
    parser.add_argument(
        "--fail-on-issues",
        action="store_true",
        help="Return non-zero when placeholders, broken links, or completeness issues exist",
    )
    args = parser.parse_args(argv)

    base_path = args.repo_root.resolve()
    if not base_path.is_dir():
        parser.error(f"--repo-root does not exist or is not a directory: {base_path}")

    report_path = args.report_path
    if not report_path.is_absolute():
        report_path = base_path / report_path

    doc_files = _collect_doc_files(base_path)
    print(f"Triple-checking {len(doc_files)} documentation files...\n")

    results = [r for fp in doc_files if (r := analyze_file(fp, base_path)) is not None]

    cats = _categorize_results(results)
    _print_console_summary(len(doc_files), results, cats)

    _write_report(report_path, len(doc_files), results, cats)
    return (
        1
        if args.fail_on_issues
        and (
            cats["total_placeholders"]
            or cats["total_broken_links"]
            or cats["total_completeness"]
        )
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
