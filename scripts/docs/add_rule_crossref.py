"""Cross-reference module AGENTS.md files with their .cursorrules counterparts.

For each module, if rules/modules/{name}.cursorrules exists, appends a
## Rule Reference section to AGENTS.md and a back-link to the .cursorrules.
Run: uv run python scripts/docs/add_rule_crossref.py [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src" / "codomyrmex"
RULES_DIR = SRC / "agentic_memory" / "rules" / "modules"
AGENTS_SECTION_MARKER = "## Rule Reference"
CURSORRULES_MARKER = "# AGENTS.md cross-reference"


def modules_with_agents_md() -> list[Path]:
    """Return all module directories that contain an AGENTS.md."""
    return sorted(p.parent for p in SRC.rglob("AGENTS.md") if p.parent.parent == SRC)


def add_crossref_to_agents_md(
    agents_md: Path, cursorrules: Path, dry_run: bool
) -> bool:
    """Append Rule Reference section to AGENTS.md if not already present."""
    content = agents_md.read_text(encoding="utf-8")
    if AGENTS_SECTION_MARKER in content:
        return False

    rel_cursorrules = cursorrules.relative_to(REPO_ROOT)
    section = (
        f"\n\n{AGENTS_SECTION_MARKER}\n\n"
        f"This module is governed by the following rule file:\n\n"
        f"- [`{rel_cursorrules}`]({rel_cursorrules})\n"
    )
    if not dry_run:
        agents_md.write_text(content + section, encoding="utf-8")
    return True


def add_crossref_to_cursorrules(
    cursorrules: Path, agents_md: Path, dry_run: bool
) -> bool:
    """Append AGENTS.md cross-reference comment to .cursorrules if not present."""
    content = cursorrules.read_text(encoding="utf-8")
    if CURSORRULES_MARKER in content:
        return False

    rel_agents_md = agents_md.relative_to(REPO_ROOT)
    comment = (
        f"\n\n{CURSORRULES_MARKER}\n# See corresponding AGENTS.md: {rel_agents_md}\n"
    )
    if not dry_run:
        cursorrules.write_text(content + comment, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true", help="Report changes without writing"
    )
    args = parser.parse_args(argv)

    agents_updated = 0
    rules_updated = 0
    skipped = 0

    for module_dir in modules_with_agents_md():
        module_name = module_dir.name
        cursorrules = RULES_DIR / f"{module_name}.cursorrules"
        agents_md = module_dir / "AGENTS.md"
        if not cursorrules.exists():
            skipped += 1
            continue
        if add_crossref_to_agents_md(agents_md, cursorrules, args.dry_run):
            agents_updated += 1
            print(
                f"{'[DRY] ' if args.dry_run else ''}Updated AGENTS.md: {agents_md.relative_to(REPO_ROOT)}"
            )
        if add_crossref_to_cursorrules(cursorrules, agents_md, args.dry_run):
            rules_updated += 1
            print(
                f"{'[DRY] ' if args.dry_run else ''}Updated .cursorrules: {cursorrules.relative_to(REPO_ROOT)}"
            )
    action = "Would update" if args.dry_run else "Updated"
    print(
        f"\n{action} {agents_updated} AGENTS.md file(s) and {rules_updated} .cursorrules file(s)."
    )
    print(f"Skipped {skipped} module(s) with no matching .cursorrules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
