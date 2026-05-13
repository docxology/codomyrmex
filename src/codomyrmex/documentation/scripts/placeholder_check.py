#!/usr/bin/env python3
"""Comprehensive placeholder content check and fix."""

import argparse
import os
import re
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# Enhanced placeholder patterns (using raw strings for proper regex escaping)
PLACEHOLDER_PATTERNS = [
    (
        r"\[Architecture description if applicable\]",
        "Architecture description placeholder",
    ),
    (r"\[Functional requirements for", "Functional requirements placeholder"),
    (
        r"\[Testing, documentation, performance, security requirements\]",
        "Requirements placeholder",
    ),
    (r"\[APIs, data structures, communication patterns\]", "Interface placeholder"),
    (r"\[How to implement within this directory\]", "Implementation placeholder"),
    (r"\[Brief description", "Brief description placeholder"),
    (r"\[Module Name\]", "Module name placeholder"),
    (r"\[MainClass\]", "Main class placeholder"),
    (r"\[module_name\]", "Module name variable placeholder"),
    (r"Contains components for the src system", "Generic placeholder description"),
    (r"Documentation files and guides\.", "Generic documentation placeholder"),
    (r"Test files and validation suites\.", "Generic test placeholder"),
]


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


def _relative_posix(path: Path, repo_root: Path) -> str:
    """Return path relative to repo_root in POSIX form."""

    return path.relative_to(repo_root).as_posix()


def find_placeholders(content: str, file_path: Path) -> list[dict]:
    """Find placeholder content in file."""
    issues = []
    for pattern, description in PLACEHOLDER_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Get context (50 chars before and after)
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end]

            issues.append(
                {
                    "pattern": pattern,
                    "description": description,
                    "match": match.group(0),
                    "position": match.start(),
                    "context": context,
                }
            )
    return issues


def _directory_label(file_path: Path) -> str:
    """Return a human-readable label for a documentation directory."""

    name = file_path.parent.name or file_path.stem
    return name.replace("_", " ").replace("-", " ").title()


def _replacement_for(file_path: Path) -> str:
    """Infer a specific one-line purpose for a generated doc file."""

    label = _directory_label(file_path)
    parts = {part.lower() for part in file_path.parts}
    if any("docs" in part or "documentation" in part for part in parts):
        return f"Documentation tooling, generated references, and publishing assets for {label}."
    if "tests" in parts or file_path.parent.name.lower().startswith("test"):
        return f"Validation coverage, fixtures, and regression checks for {label}."
    if "examples" in parts or "demos" in parts:
        return f"Executable examples and demonstrations for {label}."
    if "scripts" in parts:
        return f"Automation utilities and maintenance commands for {label}."
    return f"Module implementation, resources, and local coordination for {label}."


def fix_generic_placeholders(content: str, file_path: Path) -> str:
    """Fix generic placeholder descriptions."""
    replacement = _replacement_for(file_path)

    # Fix "Contains components for the src system"
    if "Contains components for the src system" in content:
        content = content.replace("Contains components for the src system", replacement)

    # Fix "Documentation files and guides."
    if "Documentation files and guides." in content:
        content = content.replace("Documentation files and guides.", replacement)

    # Fix "Test files and validation suites."
    if "Test files and validation suites." in content:
        content = content.replace("Test files and validation suites.", replacement)

    return content


def main():
    """Run comprehensive placeholder check."""
    parser = argparse.ArgumentParser(
        description="Find and repair generic generated documentation placeholders."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report generic placeholder fixes without writing files.",
    )
    parser.add_argument(
        "--include-submodules",
        action="store_true",
        help="Also scan paths listed in .gitmodules. Defaults to skipping them.",
    )
    args = parser.parse_args()
    base_path = args.repo_root.resolve()
    submodule_paths = _load_gitmodule_paths(base_path)

    doc_files = []
    for root, dirs, _files in os.walk(base_path):
        root_path = Path(root).resolve()
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d
            not in ["__pycache__", "node_modules", "venv", ".venv", ".git", "@output"]
        ]
        if not args.include_submodules and submodule_paths:
            dirs[:] = [
                d
                for d in dirs
                if _relative_posix(root_path / d, base_path) not in submodule_paths
            ]

        for file in ["README.md", "AGENTS.md", "SPEC.md"]:
            file_path = root_path / file
            if file_path.exists():
                doc_files.append(file_path)

    print(f"Checking {len(doc_files)} files for placeholders...\n")
    if args.dry_run:
        print("Dry run: no files will be modified.\n")

    total_issues = 0
    fixed_count = 0

    for file_path in doc_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            original = content

            # Find placeholders
            issues = find_placeholders(content, file_path)

            if issues:
                total_issues += len(issues)
                print(
                    f"\n{file_path.relative_to(base_path)}: {len(issues)} placeholder(s)"
                )
                for issue in issues[:3]:  # Show first 3
                    print(f"  - {issue['description']}: {issue['match'][:50]}")

            # Fix generic placeholders
            content = fix_generic_placeholders(content, file_path)

            if content != original:
                if not args.dry_run:
                    file_path.write_text(content, encoding="utf-8")
                fixed_count += 1
                action = "Would fix" if args.dry_run else "Fixed"
                print(f"  {action} generic placeholders")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print("\n=== SUMMARY ===")
    print(f"Total placeholder issues found: {total_issues}")
    print(f"Files with generic placeholders fixed: {fixed_count}")


if __name__ == "__main__":
    main()
