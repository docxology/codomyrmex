"""Skill Updater — regenerate tool tables in SKILL.md files.

Reads the tool registry via ``codomyrmex.agents.pai.mcp_bridge``,
builds a markdown table of all tools with inferred categories,
and rewrites the table section in the target SKILL.md file.

This module contains the core business logic. The thin CLI wrapper
is at ``scripts/pai/update_pai_skill.py``.
"""

from __future__ import annotations

import re
from pathlib import Path

from codomyrmex.agents.pai.mcp_bridge import get_tool_registry
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

DEFAULT_SKILL_PATH = Path("~/.claude/skills/Codomyrmex/SKILL.md").expanduser().resolve()


def _infer_category(name: str) -> str:
    """Infer a tool category from its name using simple heuristics."""
    # Check more specific patterns first
    if "memory" in name or "memories" in name:
        return "Memory"
    if "git" in name:
        return "Git"
    if "pai" in name:
        return "PAI"
    if "ask" in name:
        return "LLM"
    if "json" in name or "checksum" in name:
        return "Data"
    if "scan" in name or "audit" in name:
        return "Security"
    if "report" in name:
        return "Visualization"
    if "read" in name or "write" in name or "list" in name:
        return "File Ops"
    if "analyze" in name or "search" in name:
        return "Code Analysis"
    if "run" in name:
        return "Execution"
    return "General"


def update_skill_md(skill_path: Path | None = None) -> int:
    """Regenerate the tool table in *skill_path*.

    Returns 0 on success, 1 on error.
    """
    path = skill_path or DEFAULT_SKILL_PATH

    if not path.exists():
        logger.error("SKILL.md not found at %s", path)
        return 1

    logger.info("Reading %s...", path)
    content = path.read_text(encoding="utf-8")

    # 1. Get all tools
    registry = get_tool_registry()
    tools = registry.list_tools()
    tools.sort()
    logger.info("Found %d tools in registry.", len(tools))

    # 2. Build new markdown table
    table_lines = [
        "| Tool | Category | Description |",
        "|------|----------|-------------|",
    ]

    for name in tools:
        tool_data = registry.get(name)
        schema = tool_data.get("schema", {})
        desc = schema.get("description", "").split("\n")[0].strip()
        category = _infer_category(name)
        desc = desc.replace("|", "\\|")
        table_lines.append(f"| `{name}` | {category} | {desc} |")

    new_table = "\n".join(table_lines)

    # 3. Replace header count
    pattern_header = r"## Tools \(\d+\)"
    replacement_header = f"## Tools ({len(tools)})"
    content = re.sub(pattern_header, replacement_header, content)

    # 4. Replace table
    table_start_marker = "| Tool | Category | Description |"
    if table_start_marker not in content:
        logger.error("Could not find table start marker in %s", path)
        return 1

    start_idx = content.find(table_start_marker)
    lines = content[start_idx:].split("\n")
    table_end_offset = 0
    for line in lines:
        if not line.strip().startswith("|"):
            break
        table_end_offset += len(line) + 1

    pre_table = content[:start_idx]
    post_table = content[start_idx + table_end_offset :]
    new_content = pre_table + new_table + "\n" + post_table

    path.write_text(new_content, encoding="utf-8")
    logger.info("Updated %s with %d tools.", path, len(tools))
    return 0
