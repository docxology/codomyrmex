"""
Update PAI Skill Definition.

Regenerates the tool table in ~/.claude/skills/Codomyrmex/SKILL.md
to reflect all currently available static and dynamic MCP tools.
"""

import sys
import re
from pathlib import Path
from codomyrmex.agents.pai.mcp_bridge import get_tool_registry
from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error

SKILL_PATH = Path("~/.claude/skills/Codomyrmex/SKILL.md").expanduser().resolve()


def update_skill_md() -> int:
    if not SKILL_PATH.exists():
        print_error(f"SKILL.md not found at {SKILL_PATH}")
        return 1

    print_info(f"Reading {SKILL_PATH}...")
    content = SKILL_PATH.read_text()

    # 1. Get all tools
    registry = get_tool_registry()
    tools = registry.list_tools()
    tools.sort()

    print_info(f"Found {len(tools)} tools in registry.")

    # 2. Build new markdown table
    # Standard columns: Tool | Category | Description

    # We need metadata. Unfortunately get_tool_registry().get() returns just schema/handler/name.
    # It doesn't have "category" easily accessible unless we dig into _mcp_tool attr or infer it.

    # Let's try to infer category from name prefix or module inspection if possible,
    # or fallback to "General".

    table_lines = [
        "| Tool | Category | Description |",
        "|------|----------|-------------|"
    ]

    for name in tools:
        tool_data = registry.get(name)
        schema = tool_data.get("schema", {})
        desc = schema.get("description", "").split('\n')[0].strip()

        # Infer category
        category = "General"
        if name.startswith("codomyrmex."):
            suffix = name.split("codomyrmex.")[1]
            if "." in suffix:
                # e.g. codomyrmex.llm.ask (hypothetical) -> llm
                # But our tools are just codomyrmex.ask
                pass

            # Simple heuristic mapping based on known tools
            if "read" in name or "write" in name or "list" in name:
                category = "File Ops"
            elif "git" in name:
                category = "Git"
            elif "analyze" in name or "search" in name:
                category = "Code Analysis"
            elif "pai" in name:
                category = "PAI"
            elif "run" in name:
                category = "Execution"
            elif "json" in name or "checksum" in name:
                category = "Data"
            elif "ask" in name:
                category = "LLM"
            elif "memory" in name:
                category = "Memory"
            elif "scan" in name or "audit" in name:
                category = "Security"
            elif "report" in name:
                category = "Visualization"

        # Escape pipes in desc
        desc = desc.replace("|", "\\|")

        table_lines.append(f"| `{name}` | {category} | {desc} |")

    new_table = "\n".join(table_lines)

    # 3. Replace text between markers
    # We look for ## Tools (N) ... table ... \n\n

    # Regex to find the header and the table
    # Update header count too

    # Replace header: ## Tools (.*) -> ## Tools (Is)
    pattern_header = r"## Tools \(\d+\)"
    replacement_header = f"## Tools ({len(tools)})"

    content = re.sub(pattern_header, replacement_header, content)

    # Replace table
    # Look for table start after ## Tools
    # It starts with | Tool | ... and ends at next double newline or section

    # Robust way: Find start of table, find end of table.
    table_start_marker = "| Tool | Category | Description |"

    if table_start_marker not in content:
        print_error("Could not find table start marker.")
        return 1

    start_idx = content.find(table_start_marker)

    # Find end of table (empty line after start)
    # Scan line by line from start
    lines = content[start_idx:].split('\n')
    table_end_offset = 0
    for line in lines:
        if not line.strip().startswith('|'):
            break
        table_end_offset += len(line) + 1 # +1 for newline

    # Reconstruct content
    pre_table = content[:start_idx]
    post_table = content[start_idx + table_end_offset:]

    new_content = pre_table + new_table + "\n" + post_table

    SKILL_PATH.write_text(new_content)
    print_success(f"Updated {SKILL_PATH} with {len(tools)} tools.")
    return 0


def main() -> int:
    setup_logging()
    return update_skill_md()


if __name__ == "__main__":
    sys.exit(main())
