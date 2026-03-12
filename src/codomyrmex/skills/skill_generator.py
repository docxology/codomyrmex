"""Skill Generator — SKILL.md file generation for PAI skill directories.

Queries ``get_skill_manifest()`` to get all tools with their categories,
groups them by logical skill domain, and writes/updates SKILL.md files
under ``~/.claude/skills/``.  Also rebuilds the skill index via
``GenerateSkillIndex.ts`` at the end.

This module contains the core business logic.  The CLI entry-point is the
thin wrapper at ``scripts/pai/generate_skills.py``.
"""

from __future__ import annotations

import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Category → Skill group mapping, descriptions, and phase maps
# are in _skill_constants.py to keep this file under 800 LOC.
# ---------------------------------------------------------------------------
from ._skill_constants import (
    CATEGORY_GROUP_MAP,
    DEFAULT_PHASE_MAPS,
    SKILL_DESCRIPTIONS,
)

# ---------------------------------------------------------------------------
# Repo root for finding PAI.md files
# ---------------------------------------------------------------------------
_SRC_ROOT = Path(__file__).resolve().parents[1]  # src/codomyrmex/


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------


def collect_tools() -> list[dict[str, Any]]:
    """Query ``get_skill_manifest()`` and return annotated tool list."""
    from codomyrmex.agents.pai.mcp_bridge import get_skill_manifest
    from codomyrmex.agents.pai.trust_gateway import DESTRUCTIVE_TOOLS

    manifest = get_skill_manifest()
    tools: list[dict[str, Any]] = manifest.get("tools", [])

    for t in tools:
        name = t.get("name", "")
        t["trust_level"] = "TRUSTED" if name in DESTRUCTIVE_TOOLS else "VERIFIED"

    return tools


def group_by_skill(tools: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group tools by skill name using :data:`CATEGORY_GROUP_MAP`."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for tool in tools:
        cat = tool.get("category", "general")
        skill_name = CATEGORY_GROUP_MAP.get(cat)
        if skill_name is None:
            skill_name = "Codomyrmex" + "".join(
                w.capitalize() for w in cat.replace("-", "_").split("_")
            )
        groups[skill_name].append(tool)
    return dict(groups)


# ---------------------------------------------------------------------------
# Phase mapping extraction from module PAI.md files
# ---------------------------------------------------------------------------


def _find_pai_md_for_categories(categories: list[str]) -> list[Path]:
    """Find PAI.md files for module directories matching the given categories."""
    pai_mds: list[Path] = []
    for cat in categories:
        module_dir = _SRC_ROOT / cat
        pai_md = module_dir / "PAI.md"
        if pai_md.exists():
            pai_mds.append(pai_md)
    return pai_mds


def extract_phase_mapping(
    categories: list[str], skill_name: str
) -> dict[str, list[str]]:
    """Extract phase → [tool_names] from module PAI.md files.

    Falls back to :data:`DEFAULT_PHASE_MAPS` if no PAI.md found or no matches.
    Merges dynamic extraction with hardcoded defaults.
    """
    phase_map: dict[str, list[str]] = defaultdict(list)

    pai_mds = _find_pai_md_for_categories(categories)
    for pai_md in pai_mds:
        try:
            content = pai_md.read_text(encoding="utf-8")
        except OSError:
            continue

        for phase in (
            "OBSERVE",
            "THINK",
            "PLAN",
            "BUILD",
            "EXECUTE",
            "VERIFY",
            "LEARN",
        ):
            pattern = rf"\|\s*\*\*{phase}\*\*\s*\|\s*(.+?)\s*\|"
            for match in re.finditer(pattern, content):
                cell = match.group(1)
                tool_names = re.findall(r"`([a-z_][a-z0-9_]*)`", cell)
                for t in tool_names:
                    if t not in phase_map[phase]:
                        phase_map[phase].append(t)

    defaults = DEFAULT_PHASE_MAPS.get(skill_name, {})
    for phase, tools_list in defaults.items():
        if phase not in phase_map or not phase_map[phase]:
            phase_map[phase] = list(tools_list)

    return dict(phase_map)


# ---------------------------------------------------------------------------
# Manual section preservation
# ---------------------------------------------------------------------------


def extract_keep_blocks(existing_content: str) -> list[str]:
    """Extract ``<!-- keep-start -->`` … ``<!-- keep-end -->`` blocks."""
    pattern = r"<!--\s*keep-start\s*-->(.*?)<!--\s*keep-end\s*-->"
    return re.findall(pattern, existing_content, re.DOTALL)


# ---------------------------------------------------------------------------
# SKILL.md rendering
# ---------------------------------------------------------------------------


def _build_trust_note(tools: list[dict[str, Any]]) -> str:
    trusted = [t["name"] for t in tools if t.get("trust_level") == "TRUSTED"]
    if not trusted:
        return ""
    tool_list = ", ".join(f"`{n}`" for n in trusted[:5])
    if len(trusted) > 5:
        tool_list += f" and {len(trusted) - 5} more"
    return (
        "\n> [!WARNING]\n"
        f"> The following tools are **TRUSTED** (destructive) and require "
        f"`/codomyrmexTrust` before use: {tool_list}\n"
    )


def _build_common_operations(tools: list[dict[str, Any]], skill_name: str) -> str:
    if not tools:
        return ""
    sample = tools[:3]
    lines = [
        "## Common Operations\n",
        "```python",
        "from codomyrmex.agents.pai import trusted_call_tool\n",
    ]
    for t in sample:
        name = t["name"]
        schema = t.get("input_schema", {})
        required = schema.get("required", []) if isinstance(schema, dict) else []
        if required:
            args = ", ".join(f'{k}="..."' for k in required[:3])
            lines.append(f'result = trusted_call_tool("{name}", {args})')
        else:
            lines.append(f'result = trusted_call_tool("{name}")')
    lines.append("```")
    return "\n".join(lines)


def _build_key_tools_table(tools: list[dict[str, Any]]) -> str:
    rows = [
        "## Key Tools\n",
        "| Tool | Description | Trust Level |",
        "|------|-------------|-------------|",
    ]
    for t in sorted(tools, key=lambda x: x["name"]):
        name = t["name"]
        desc = (t.get("description") or "").split("\n")[0].strip()
        if len(desc) > 80:
            desc = desc[:77] + "..."
        desc = desc.replace("|", "\\|")
        trust = t.get("trust_level", "VERIFIED")
        rows.append(f"| `{name}` | {desc} | {trust} |")
    return "\n".join(rows)


def _build_phase_mapping(phase_map: dict[str, list[str]]) -> str:
    if not phase_map:
        return ""
    ordered_phases = ["OBSERVE", "THINK", "PLAN", "BUILD", "EXECUTE", "VERIFY", "LEARN"]
    rows = ["## Algorithm Phase Mapping\n", "| Phase | Tools |", "|-------|-------|"]
    for phase in ordered_phases:
        tools_list = phase_map.get(phase, [])
        if tools_list:
            tool_str = ", ".join(f"`{t}`" for t in tools_list)
            rows.append(f"| **{phase}** | {tool_str} |")
    return "\n".join(rows)


def _auto_description(skill_name: str, categories: list[str]) -> str:
    cat_str = ", ".join(categories)
    return (
        f"{skill_name} operations via Codomyrmex. "
        f"USE WHEN user wants {cat_str} operations, "
        f"or uses any codomyrmex {cat_str} tools."
    )


def render_skill_md(
    skill_name: str,
    tools: list[dict[str, Any]],
    categories: list[str],
    existing_content: str = "",
) -> str:
    """Render a complete SKILL.md file for the given skill group."""
    description = SKILL_DESCRIPTIONS.get(
        skill_name, _auto_description(skill_name, categories)
    )
    phase_map = extract_phase_mapping(categories, skill_name)
    keep_blocks = extract_keep_blocks(existing_content)
    module_str = ", ".join(f"`{c}`" for c in sorted(set(categories)))
    summary = f"{skill_name} operations using Codomyrmex modules: {module_str}."

    parts = [
        "---",
        f"name: {skill_name}",
        f"description: {description}",
        "---",
        f"# {skill_name}",
        "",
        summary,
        "",
    ]

    trust_note = _build_trust_note(tools)
    if trust_note:
        parts.append(trust_note)

    common_ops = _build_common_operations(tools, skill_name)
    if common_ops:
        parts.append(common_ops)
        parts.append("")

    tools_table = _build_key_tools_table(tools)
    if tools_table:
        parts.append(tools_table)
        parts.append("")

    phase_section = _build_phase_mapping(phase_map)
    if phase_section:
        parts.append(phase_section)
        parts.append("")

    for block in keep_blocks:
        parts.append(f"<!-- keep-start -->{block}<!-- keep-end -->")
        parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Write and index rebuild
# ---------------------------------------------------------------------------


def write_skill(
    skill_name: str,
    content: str,
    output_dir: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> None:
    """Write (or print) the SKILL.md for a skill."""
    if dry_run:
        print(f"\n{'=' * 70}")
        print(f"DRY RUN: {output_dir / skill_name / 'SKILL.md'}")
        print("=" * 70)
        print(content)
        return

    skill_dir = output_dir / skill_name
    skill_path = skill_dir / "SKILL.md"

    if skill_path.exists() and not force:
        print(f"  [merge] {skill_path}")
    else:
        print(f"  [write] {skill_path}")

    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(content, encoding="utf-8")


def rebuild_index(output_dir: Path) -> None:
    """Run ``GenerateSkillIndex.ts`` to rebuild the skill index."""
    index_script = (
        Path.home() / ".claude" / "skills" / "PAI" / "Tools" / "GenerateSkillIndex.ts"
    )
    if not index_script.exists():
        logger.info("GenerateSkillIndex.ts not found at %s, skipping", index_script)
        return

    logger.info("Running %s...", index_script)
    result = subprocess.run(
        ["bun", str(index_script)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode == 0:
        logger.info("Skill index rebuilt.")
    else:
        logger.warning(
            "GenerateSkillIndex.ts exited %d: %s",
            result.returncode,
            result.stderr[:200],
        )


# ---------------------------------------------------------------------------
# High-level entry point (called by thin CLI wrapper)
# ---------------------------------------------------------------------------


def generate_skill_files(
    *,
    category: str | None = None,
    dry_run: bool = False,
    output_dir: str | Path | None = None,
    no_rebuild_index: bool = False,
    force: bool = False,
    list_categories: bool = False,
) -> int:
    """Generate SKILL.md files for all (or one) skill groups.

    Returns 0 on success, non-zero on error. This is the main entry point
    used by the thin CLI wrapper at ``scripts/pai/generate_skills.py``.
    """
    out = Path(output_dir or "~/.claude/skills").expanduser().resolve()

    print("Collecting tools from get_skill_manifest()...")
    try:
        tools = collect_tools()
    except ImportError as exc:
        print(f"ERROR: Could not import codomyrmex: {exc}")
        return 1

    print(f"  Found {len(tools)} tools.")

    if list_categories:
        cats: dict[str, int] = defaultdict(int)
        for t in tools:
            cats[t.get("category", "general")] += 1
        print("\nDiscovered categories:")
        for cat, count in sorted(cats.items()):
            skill = CATEGORY_GROUP_MAP.get(cat, f"Codomyrmex{cat.title()}")
            print(f"  {cat:<28} ({count:3} tools) → {skill}")
        return 0

    groups = group_by_skill(tools)
    print(f"  Grouped into {len(groups)} skills: {', '.join(sorted(groups))}")

    if category:
        if category not in groups:
            print(
                f"ERROR: Skill '{category}' not found. Known: {', '.join(sorted(groups))}"
            )
            return 1
        groups = {category: groups[category]}

    skill_to_cats: dict[str, list[str]] = defaultdict(list)
    for cat, skill_name in CATEGORY_GROUP_MAP.items():
        skill_to_cats[skill_name].append(cat)

    generated = 0
    for skill_name, skill_tools in sorted(groups.items()):
        categories_list = skill_to_cats.get(skill_name, [])
        if not categories_list:
            categories_list = [skill_name.replace("Codomyrmex", "").lower()]

        existing_path = out / skill_name / "SKILL.md"
        existing_content = ""
        if existing_path.exists() and not force:
            existing_content = existing_path.read_text(encoding="utf-8")

        content = render_skill_md(
            skill_name, skill_tools, categories_list, existing_content
        )
        write_skill(skill_name, content, out, dry_run=dry_run, force=force)
        generated += 1

    if not dry_run:
        print(f"\nGenerated {generated} SKILL.md files in {out}")
        if not no_rebuild_index:
            rebuild_index(out)

    return 0
