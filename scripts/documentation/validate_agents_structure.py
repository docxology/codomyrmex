#!/usr/bin/env python3
"""Validate AGENTS.md structure against standards.

Ensures AGENTS.md files follow the expected structure:
- Required sections
- Proper formatting
- AI agent instructions are complete
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

REQUIRED_SECTIONS = [
    "Purpose",
    "Key Files",
    "Dependencies",
    "Development Guidelines",
]

OPTIONAL_SECTIONS = [
    "Code Style",
    "Testing",
    "Integration Points",
    "Common Tasks",
]

# Headings that satisfy a required section (exact title first, then common hub aliases).
_SECTION_ALIASES: dict[str, list[str]] = {
    "Key Files": [
        r"^#+\s+Key Files\b",
        r"^#+\s+Agent Documentation Index\b",
        r"^#+\s+Documentation files\b",
        r"^#+\s+Documentation Files\b",
        r"^#+\s+Active Components\b",
        r"^#+\s+Key Components\b",
        r"^#+\s+File Naming Convention\b",
        r"^#+\s+Key Sub-components\b",
        r"^#+\s+Components\b",
        r"^#+\s+Module Structure\b",
        r"^#+\s+Capabilities\b",
        r"^#+\s+Contents \(by file\)\s*$",
        r"^#+\s+Key Capabilities\b",
        r"^#+\s+Key Documents in This Directory\b",
    ],
    "Dependencies": [
        r"^#+\s+Dependencies\b",
        r"^#+\s+Integration Points\b",
        r"^#+\s+Sentinel Configuration\b",
        r"^#+\s+Navigation\b",
        r"^#+\s+Navigation Links\b",
    ],
    "Development Guidelines": [
        r"^#+\s+Development Guidelines\b",
        r"^#+\s+Operating Contracts\b",
        r"^#+\s+Operating contracts\b",
        r"^#+\s+Agent Operating Rules\b",
        r"^#+\s+Workflow\b",
        r"^#+\s+Zero-Mock Policy\b",
        r"^#+\s+Conventions\b",
        r"^#+\s+Protocol Directives\b",
        r"^#+\s+Diagram conventions\b",
    ],
}


def _agents_path_skipped(rel_posix: str) -> bool:
    """Skip vendor, test harness, and embedded app trees (AGENTS stubs are non-canonical)."""
    if "src/codomyrmex/skills/skills/upstream/" in rel_posix:
        return True
    if "src/codomyrmex/skills/skills/custom/" in rel_posix:
        return True
    if rel_posix.startswith("src/codomyrmex/tests/"):
        return True
    if "src/codomyrmex/agents/mission_control/app/" in rel_posix:
        return True
    if "src/codomyrmex/agents/open_gauss/" in rel_posix:
        return True
    if "src/codomyrmex/agents/ghost_architecture/" in rel_posix:
        return True
    if ".egg-info/" in rel_posix:
        return True
    if "/.next/" in rel_posix:
        return True
    return False


def _section_satisfied(canonical: str, content: str) -> bool:
    if canonical == "Purpose":
        return bool(
            re.search(r"^#+\s+Purpose\b", content, re.MULTILINE | re.IGNORECASE)
            or re.search(
                r"^#+\s+Module Purpose\b", content, re.MULTILINE | re.IGNORECASE
            )
        )
    for pat in _SECTION_ALIASES.get(canonical, []):
        if re.search(pat, content, re.MULTILINE | re.IGNORECASE):
            return True
    pattern = rf"^#+\s+{re.escape(canonical)}\b"
    return bool(re.search(pattern, content, re.MULTILINE | re.IGNORECASE))


class ValidationResult(NamedTuple):
    """Result of AGENTS.md validation."""

    file: str
    valid: bool
    missing_sections: list
    warnings: list
    score: int  # 0-100


def validate_agents_file(file_path: Path, repo_root: Path) -> ValidationResult:
    """Validate a single AGENTS.md file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return ValidationResult(str(file_path), False, [], [str(e)], 0)

    file_str = str(file_path.relative_to(repo_root))
    missing_sections = []
    warnings = []
    score = 100

    # Check for required sections (exact or approved alias headings)
    for section in REQUIRED_SECTIONS:
        if not _section_satisfied(section, content):
            missing_sections.append(section)
            score -= 20

    # Check for optional sections (warn if missing, don't penalize)
    for section in OPTIONAL_SECTIONS:
        pattern = rf"^#+\s+{re.escape(section)}"
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            warnings.append(f"Consider adding '{section}' section")

    # Check minimum content
    if len(content) < 200:
        warnings.append("File appears too short")
        score -= 10

    # Check for headings
    headings = re.findall(r"^#+\s+.+$", content, re.MULTILINE)
    if len(headings) < 3:
        warnings.append("File has very few sections")
        score -= 10

    # Check for code blocks or file references
    has_code = "```" in content
    has_file_refs = re.search(r"`[a-zA-Z_/]+\.[a-zA-Z]+`", content)
    if not has_code and not has_file_refs:
        warnings.append("No code blocks or file references found")

    valid = len(missing_sections) == 0

    return ValidationResult(file_str, valid, missing_sections, warnings, max(0, score))


def validate_agents_structure(
    repo_root: Path, output_dir: Path | None = None, output_format: str = "both"
) -> int:
    """Validate all AGENTS.md files in the repository."""
    print("🤖 Validating AGENTS.md structure...\n")

    if output_dir is None:
        output_dir = repo_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[ValidationResult] = []

    # Directories to completely ignore during validation
    IGNORE_DIRS = {
        ".git",
        "node_modules",
        "output",
        "build",
        "dist",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".cursor",
        ".vscode",
        ".cache",
        "vendor",
        ".claude",
        ".gitnexus",
        ".sisyphus",
        ".benchmarks",
        ".pipelines",
        ".workflows",
        ".github",
        ".docusaurus",
        "@output",
        ".codomyrmex",
    }

    # Find all AGENTS.md files
    agents_files = []
    for f in repo_root.rglob("AGENTS.md"):
        # Check if any parent directory is in IGNORE_DIRS
        if set(f.parts).intersection(IGNORE_DIRS):
            continue
        rel = f.relative_to(repo_root).as_posix()
        if _agents_path_skipped(rel):
            continue
        agents_files.append(f)

    if not agents_files:
        print("⚠️  No AGENTS.md files found")
        return 0

    print(f"📄 Found {len(agents_files)} AGENTS.md files")

    for agents_file in agents_files:
        result = validate_agents_file(agents_file, repo_root)
        results.append(result)

    # Calculate stats
    valid_count = sum(1 for r in results if r.valid)
    avg_score = sum(r.score for r in results) / len(results) if results else 0

    # Output results
    if output_format in ("json", "both"):
        json_path = output_dir / "agents_validation.json"
        with open(json_path, "w") as f:
            json.dump([r._asdict() for r in results], f, indent=2)
        print(f"📄 JSON report: {json_path}")

    if output_format in ("markdown", "both"):
        md_path = output_dir / "agents_validation.md"
        with open(md_path, "w") as f:
            f.write("# AGENTS.md Validation Report\n\n")
            f.write(f"- **Valid Files**: {valid_count}/{len(results)}\n")
            f.write(f"- **Average Score**: {avg_score:.1f}/100\n\n")

            invalid = [r for r in results if not r.valid]
            if invalid:
                f.write("## Invalid Files\n\n")
                for r in invalid:
                    f.write(f"### `{r.file}` - {r.score}/100\n")
                    f.write("**Missing Sections:**\n")
                    f.writelines(f"- {section}\n" for section in r.missing_sections)
                    f.write("\n")
        print(f"📄 Markdown report: {md_path}")

    # Summary
    print(f"\n✅ Valid: {valid_count}/{len(results)}")
    print(f"📊 Average Score: {avg_score:.1f}/100")

    invalid = [r for r in results if not r.valid]
    if invalid:
        print("\n❌ Invalid AGENTS.md files:")
        for r in invalid:
            print(f"   {r.file}: missing {', '.join(r.missing_sections)}")
        return 1 if "--fail-on-invalid" in sys.argv else 0

    print("\n✅ All AGENTS.md files are valid!")
    return 0


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "documentation"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/documentation/config.yaml")

    parser = argparse.ArgumentParser(description="Validate AGENTS.md structure")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--format", choices=["json", "markdown", "both"], default="both"
    )
    parser.add_argument("--fail-on-invalid", action="store_true")

    args = parser.parse_args()
    return validate_agents_structure(args.repo_root, args.output, args.format)


if __name__ == "__main__":
    sys.exit(main())
