"""Auto-Generate Codomyrmex SKILL.md Files.

Thin CLI wrapper — all business logic lives in
``codomyrmex.skills.skill_generator``.

Usage::

    uv run python scripts/pai/generate_skills.py [options]

    --category CATEGORY   Generate only this skill group (default: all)
    --dry-run             Print SKILL.md to stdout, no writes
    --output-dir DIR      Override output dir (default: ~/.claude/skills/)
    --no-rebuild-index    Skip GenerateSkillIndex.ts at end
    --force               Overwrite existing skills (default: merge)
    --list-categories     Show all discovered categories and exit
"""

import sys
import argparse

from codomyrmex.skills.skill_generator import generate_skill_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--category", metavar="SKILL", help="Generate only this skill group")
    parser.add_argument("--dry-run", action="store_true", help="Print SKILL.md to stdout; no writes")
    parser.add_argument("--output-dir", metavar="DIR", default="~/.claude/skills", help="Output directory")
    parser.add_argument("--no-rebuild-index", action="store_true", help="Skip GenerateSkillIndex.ts")
    parser.add_argument("--force", action="store_true", help="Overwrite existing skills")
    parser.add_argument("--list-categories", action="store_true", help="Show all discovered categories")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return generate_skill_files(
        category=args.category,
        dry_run=args.dry_run,
        output_dir=args.output_dir,
        no_rebuild_index=args.no_rebuild_index,
        force=args.force,
        list_categories=args.list_categories,
    )


if __name__ == "__main__":
    sys.exit(main())
