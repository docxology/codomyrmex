"""
PAI documentation generation and updates.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Any

MAX_STUB_LINES = 55

# Layer classification for modules
FOUNDATION = {"logging_monitoring", "environment_setup", "model_context_protocol", "terminal_interface"}
CORE = {
    "agents", "static_analysis", "coding", "llm", "pattern_matching", "git_operations",
    "search", "documents", "agentic_memory", "cerebrum", "graph_rag",
}
SERVICE = {
    "build_synthesis", "documentation", "ci_cd_automation", "containerization",
    "orchestrator", "events", "logistics",
}
APPLICATION = {"cli", "system_discovery", "website", "ide"}


def get_layer(module_name: str) -> str:
    """Determine module layer."""
    if module_name in FOUNDATION:
        return "Foundation"
    elif module_name in CORE:
        return "Core"
    elif module_name in SERVICE:
        return "Service"
    elif module_name in APPLICATION:
        return "Application"
    return "Extended"


def extract_exports(init_path: Path) -> Dict[str, Any]:
    """Extract exports from __init__.py by parsing __all__ and import statements."""
    if not init_path.exists():
        return {"all": [], "classes": [], "functions": [], "docstring": ""}

    content = init_path.read_text(encoding="utf-8")

    # Extract docstring
    docstring = ""
    try:
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree) or ""
    except SyntaxError:
        pass

    # Extract __all__ list
    all_exports = []
    all_match = re.search(r'__all__\s*=\s*\[([^\]]+)\]', content, re.DOTALL)
    if all_match:
        items = re.findall(r'"([^"]+)"|\'([^\']+)\'', all_match.group(1))
        all_exports = [a or b for a, b in items]

    # Classify exports
    classes = []
    functions = []
    for name in all_exports:
        if name == "cli_commands":
            continue
        if name[0].isupper() and not name.startswith("SUPPORTED"):
            classes.append(name)
        elif not name.startswith("_"):
            functions.append(name)

    return {
        "all": all_exports,
        "classes": classes,
        "functions": functions,
        "docstring": docstring,
    }


def extract_readme_description(readme_path: Path) -> str:
    """Extract the first paragraph from README.md."""
    if not readme_path.exists():
        return ""
    content = readme_path.read_text(encoding="utf-8")
    # Skip the title line, get first paragraph
    lines = content.split("\n")
    desc_lines = []
    started = False
    for line in lines:
        if line.startswith("#"):
            if started:
                break
            started = True
            continue
        if started and line.strip():
            desc_lines.append(line.strip())
        elif started and not line.strip() and desc_lines:
            break
    return " ".join(desc_lines)[:300]


def humanize_name(module_name: str) -> str:
    """Convert module_name to Title Case."""
    return module_name.replace("_", " ").title()


def infer_pai_phase(module_name: str, functions: List[str], classes: List[str]) -> Dict[str, str]:
    """Infer PAI Algorithm phase mapping from module content."""
    phases = {}
    all_names = " ".join(functions + classes).lower()

    if any(w in all_names for w in ["get_", "list_", "read_", "search", "discover", "status", "fetch"]):
        phases["OBSERVE"] = "Data gathering and state inspection"
    if any(w in all_names for w in ["analyz", "reason", "match", "pattern", "cerebr", "graph"]):
        phases["THINK"] = "Analysis and reasoning"
    if any(w in all_names for w in ["plan", "schedule", "orchestrat", "workflow", "dag"]):
        phases["PLAN"] = "Workflow planning and scheduling"
    if any(w in all_names for w in ["generat", "create", "build", "write_", "render", "compil"]):
        phases["BUILD"] = "Artifact creation and code generation"
    if any(w in all_names for w in ["execut", "run_", "deploy", "send", "push", "process"]):
        phases["EXECUTE"] = "Execution and deployment"
    if any(w in all_names for w in ["verif", "validat", "check", "test", "scan", "audit", "lint"]):
        phases["VERIFY"] = "Validation and quality checks"
    if any(w in all_names for w in ["learn", "store", "memory", "log", "metric", "record"]):
        phases["LEARN"] = "Learning and knowledge capture"

    if not phases:
        phases["EXECUTE"] = "General module operations"

    return phases


def generate_pai_md(module_name: str, module_dir: Path) -> str:
    """Generate improved PAI.md content for a module."""
    init_path = module_dir / "__init__.py"
    readme_path = module_dir / "README.md"

    exports = extract_exports(init_path)
    readme_desc = extract_readme_description(readme_path)
    human_name = humanize_name(module_name)
    layer = get_layer(module_name)
    phases = infer_pai_phase(module_name, exports["functions"], exports["classes"])

    # Build overview
    overview = exports["docstring"].split("\n")[0] if exports["docstring"] else ""
    if not overview:
        overview = readme_desc or f"The {human_name} module provides capabilities for the codomyrmex ecosystem."

    # Build the document
    sections = []

    # Header
    sections.append(f"# Personal AI Infrastructure — {human_name} Module\n")
    sections.append(f"**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026\n")

    # Overview
    sections.append(f"## Overview\n")
    article = "an" if layer[0] in "AEIOU" else "a"
    sections.append(f"{overview} This is {article} **{layer} Layer** module.\n")

    # PAI Capabilities with real code examples
    sections.append(f"## PAI Capabilities\n")

    if exports["classes"] or exports["functions"]:
        # Code example
        imports = []
        if exports["classes"][:3]:
            imports.extend(exports["classes"][:3])
        if exports["functions"][:3]:
            imports.extend(exports["functions"][:3])

        if imports:
            import_str = ", ".join(imports)
            sections.append(f"```python\nfrom codomyrmex.{module_name} import {import_str}\n```\n")

    # Key Exports table
    if exports["all"]:
        sections.append(f"## Key Exports\n")
        sections.append(f"| Export | Type | Purpose |")
        sections.append(f"|--------|------|---------|")
        for name in exports["all"][:15]:  # Limit to 15 to keep reasonable
            if name == "cli_commands":
                continue
            etype = "Class" if name[0].isupper() and not name.startswith("SUPPORTED") else "Function/Constant"
            purpose = name.replace("_", " ").capitalize()
            sections.append(f"| `{name}` | {etype} | {purpose} |")
        if len(exports["all"]) > 15:
            sections.append(f"\n*Plus {len(exports['all']) - 15} additional exports.*\n")
        sections.append("")

    # PAI Algorithm Phase Mapping
    sections.append(f"## PAI Algorithm Phase Mapping\n")
    sections.append(f"| Phase | {human_name} Contribution |")
    sections.append(f"|-------|{'-' * 30}|")
    for phase, desc in phases.items():
        sections.append(f"| **{phase}** | {desc} |")
    sections.append("")

    # Architecture Role
    sections.append(f"## Architecture Role\n")
    sections.append(f"**{layer} Layer** — Part of the codomyrmex layered architecture.\n")

    # Navigation
    sections.append(f"## Navigation\n")
    sections.append(f"- **Self**: [PAI.md](PAI.md)")
    sections.append(f"- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map")
    sections.append(f"- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc")
    sections.append(f"- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)")

    return "\n".join(sections) + "\n"


def update_pai_docs(src_dir: Path, apply: bool = False, max_lines: int = MAX_STUB_LINES) -> None:
    """Batch update stub PAI.md files."""
    updated = 0
    skipped = 0
    errors = 0

    if not src_dir.exists():
        print(f"Error: Source directory {src_dir} does not exist.")
        return

    for pai_path in sorted(src_dir.glob("*/PAI.md")):
        module_dir = pai_path.parent
        module_name = module_dir.name

        # Skip non-module directories
        if module_name.startswith("_") or module_name == "tests":
            continue

        # Check if it's a stub
        try:
            current_lines = len(pai_path.read_text(encoding="utf-8").splitlines())
            if current_lines > max_lines:
                skipped += 1
                continue

            new_content = generate_pai_md(module_name, module_dir)
            new_lines = len(new_content.splitlines())

            if apply:
                pai_path.write_text(new_content, encoding="utf-8")
                print(f"  UPDATED  {module_name}/PAI.md ({current_lines} -> {new_lines} lines)")
            else:
                print(f"  WOULD UPDATE  {module_name}/PAI.md ({current_lines} -> {new_lines} lines)")

            updated += 1
        except Exception as e:
            print(f"  ERROR    {module_name}/PAI.md: {e}")
            errors += 1

    print(f"\n{'Applied' if apply else 'Dry run'}: {updated} updated, {skipped} skipped (already good), {errors} errors")
