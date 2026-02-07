#!/usr/bin/env python3
"""Enrich src-level SPEC.md files and create missing submodule docs.

1. Fixes wrong SPEC.md titles (coding, tests)
2. Adds testing sections to SPEC.md files that lack them
3. Adds code blocks (API examples) to SPEC.md files without them
4. Creates missing README.md and AGENTS.md for submodules
"""
import ast
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "codomyrmex")


def get_module_info(mod_path):
    """Extract module info from __init__.py."""
    init = os.path.join(mod_path, "__init__.py")
    info = {"classes": [], "functions": [], "desc": "", "name": os.path.basename(mod_path)}
    if not os.path.exists(init):
        return info
    try:
        content = open(init).read()
        tree = ast.parse(content)
    except Exception:
        return info

    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
        info["desc"] = tree.body[0].value.value.strip().split("\n")[0]

    seen_c, seen_f = set(), set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name not in seen_c:
            doc = ast.get_docstring(node) or ""
            info["classes"].append((node.name, doc.split("\n")[0] if doc else ""))
            seen_c.add(node.name)
        elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_") and node.name not in seen_f:
            doc = ast.get_docstring(node) or ""
            info["functions"].append((node.name, doc.split("\n")[0] if doc else ""))
            seen_f.add(node.name)

    if not info["classes"] and not info["functions"]:
        for f in sorted(os.listdir(mod_path)):
            if not f.endswith(".py") or f == "__init__.py":
                continue
            try:
                sub_tree = ast.parse(open(os.path.join(mod_path, f)).read())
                for node in sub_tree.body:
                    if isinstance(node, ast.ClassDef) and node.name not in seen_c:
                        doc = ast.get_docstring(node) or ""
                        info["classes"].append((node.name, doc.split("\n")[0] if doc else ""))
                        seen_c.add(node.name)
                    elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_") and node.name not in seen_f:
                        doc = ast.get_docstring(node) or ""
                        info["functions"].append((node.name, doc.split("\n")[0] if doc else ""))
                        seen_f.add(node.name)
            except Exception:
                pass
            if len(info["classes"]) >= 5 or len(info["functions"]) >= 5:
                break

    return info


def get_display_name(mod_name):
    """Convert module name to display name."""
    display_map = {
        "api": "API",
        "cli": "CLI",
        "llm": "LLM",
        "ide": "IDE",
        "fpf": "FPF",
        "i18n": "i18n",
        "ci_cd_automation": "CI/CD Automation",
        "utils": "Utilities",
        "logging_monitoring": "Logging & Monitoring",
        "tree_sitter": "Tree-sitter",
        "auth": "Authentication",
        "dark": "Dark Modes",
        "coding": "Coding",
        "tests": "Tests",
        "cerebrum": "CEREBRUM",
        "graph_rag": "Graph RAG",
    }
    return display_map.get(mod_name, mod_name.replace("_", " ").title())


def fix_spec_title(mod_name):
    """Fix wrong SPEC.md titles."""
    spec_path = os.path.join(SRC, mod_name, "SPEC.md")
    if not os.path.exists(spec_path):
        return False
    with open(spec_path) as f:
        content = f.read()
    first_line = content.split("\n")[0]
    display = get_display_name(mod_name)
    expected_prefix = f"# {display}"
    if display.lower() not in first_line.lower() and mod_name.lower() not in first_line.lower():
        new_title = f"# {display} — Functional Specification"
        content = content.replace(first_line, new_title, 1)
        with open(spec_path, "w") as f:
            f.write(content)
        return True
    return False


def enrich_spec(mod_name, info):
    """Add missing sections to SPEC.md."""
    spec_path = os.path.join(SRC, mod_name, "SPEC.md")
    if not os.path.exists(spec_path):
        return False
    with open(spec_path) as f:
        content = f.read()

    modified = False
    content_lower = content.lower()

    # Add testing section if missing
    if "test" not in content_lower:
        testing = f"\n## Testing\n\n```bash\nuv run python -m pytest src/codomyrmex/tests/ -k {mod_name} -v\n```\n"
        content = content.rstrip() + "\n" + testing
        modified = True

    # Add API code block if no code blocks exist
    if "```" not in content:
        code = f"\n## API Usage\n\n```python\n"
        if info["classes"]:
            imports = ", ".join(c[0] for c in info["classes"][:3])
            code += f"from codomyrmex.{mod_name} import {imports}\n"
        elif info["functions"]:
            imports = ", ".join(f_[0] for f_ in info["functions"][:3])
            code += f"from codomyrmex.{mod_name} import {imports}\n"
        else:
            code += f"import codomyrmex.{mod_name}\n"
        code += "```\n"
        # Insert before Testing section if it exists
        if "## Testing" in content:
            content = content.replace("## Testing", code + "\n## Testing")
        else:
            content = content.rstrip() + "\n" + code
        modified = True

    # Add dependencies mention if missing
    if "depend" not in content_lower and "require" not in content_lower:
        deps = f"\n## Dependencies\n\nSee `src/codomyrmex/{mod_name}/__init__.py` for import dependencies.\n"
        if "## Testing" in content:
            content = content.replace("## Testing", deps + "\n## Testing")
        else:
            content = content.rstrip() + "\n" + deps
        modified = True

    if modified:
        with open(spec_path, "w") as f:
            f.write(content)

    return modified


def create_submodule_readme(parent, sub, info):
    """Create README.md for a submodule."""
    sub_path = os.path.join(SRC, parent, sub, "README.md")
    display = get_display_name(sub)
    parent_display = get_display_name(parent)

    content = f"# {display}\n\n"
    content += f"**Module**: `codomyrmex.{parent}.{sub}` | **Status**: Active\n\n"
    content += f"## Overview\n\n"
    content += f"{info['desc'] or f'{display} submodule of {parent_display}.'}\n\n"

    if info["classes"] or info["functions"]:
        content += "## Key Exports\n\n"
        if info["classes"]:
            for name, doc in info["classes"][:5]:
                content += f"- **`{name}`** — {doc or name}\n"
            content += "\n"
        if info["functions"]:
            for name, doc in info["functions"][:5]:
                content += f"- **`{name}()`** — {doc or name}\n"
            content += "\n"

    content += "## Quick Start\n\n"
    content += "```python\n"
    if info["classes"]:
        imports = ", ".join(c[0] for c in info["classes"][:3])
        content += f"from codomyrmex.{parent}.{sub} import {imports}\n"
    elif info["functions"]:
        imports = ", ".join(fn[0] for fn in info["functions"][:3])
        content += f"from codomyrmex.{parent}.{sub} import {imports}\n"
    else:
        content += f"import codomyrmex.{parent}.{sub}\n"
    content += "```\n\n"
    content += "## Navigation\n\n"
    content += f"- **📁 Parent**: [{parent_display}](../README.md)\n"
    content += f"- **🏠 Root**: [codomyrmex](../../../../README.md)\n"

    with open(sub_path, "w") as f:
        f.write(content)


def create_submodule_agents(parent, sub, info):
    """Create AGENTS.md for a submodule."""
    sub_path = os.path.join(SRC, parent, sub, "AGENTS.md")
    display = get_display_name(sub)
    parent_display = get_display_name(parent)

    content = f"# Agent Guidelines — {display}\n\n"
    content += f"## Overview\n\n"
    content += f"{info['desc'] or f'{display} submodule for agent operations.'}\n\n"

    content += "## Operating Contracts\n\n"
    content += f"- Maintain alignment with the parent `{parent}` module.\n"
    content += "- Follow existing code patterns and conventions.\n"
    content += "- Record outcomes in shared telemetry.\n\n"

    content += "## Common Patterns\n\n"
    content += "```python\n"
    if info["classes"]:
        imports = ", ".join(c[0] for c in info["classes"][:3])
        content += f"from codomyrmex.{parent}.{sub} import {imports}\n"
    elif info["functions"]:
        imports = ", ".join(fn[0] for fn in info["functions"][:3])
        content += f"from codomyrmex.{parent}.{sub} import {imports}\n"
    else:
        content += f"import codomyrmex.{parent}.{sub}\n"
    content += "```\n\n"

    content += "## Navigation\n\n"
    content += f"- **📁 Parent**: [{parent_display}](../AGENTS.md)\n"
    content += f"- **🏠 Root**: [codomyrmex](../../../../AGENTS.md)\n"

    with open(sub_path, "w") as f:
        f.write(content)


def main():
    modules = sorted(
        d for d in os.listdir(SRC)
        if os.path.isdir(os.path.join(SRC, d)) and d != "__pycache__"
    )

    # Phase 1: Fix SPEC titles
    title_fixed = 0
    for mod in modules:
        if fix_spec_title(mod):
            title_fixed += 1
            sys.stdout.write("T")
        sys.stdout.flush()
    print(f"\n✅ SPEC.md titles fixed: {title_fixed}")

    # Phase 2: Enrich SPEC.md
    spec_fixed = 0
    for mod in modules:
        info = get_module_info(os.path.join(SRC, mod))
        if enrich_spec(mod, info):
            spec_fixed += 1
            sys.stdout.write("S")
        else:
            sys.stdout.write(".")
        sys.stdout.flush()
    print(f"\n✅ SPEC.md enriched: {spec_fixed}")

    # Phase 3: Create missing submodule docs
    sub_readme = 0
    sub_agents = 0
    for mod in modules:
        mod_path = os.path.join(SRC, mod)
        for sub in sorted(os.listdir(mod_path)):
            sp = os.path.join(mod_path, sub)
            if not os.path.isdir(sp) or sub == "__pycache__":
                continue
            if not os.path.exists(os.path.join(sp, "__init__.py")):
                continue
            info = get_module_info(sp)
            if not os.path.exists(os.path.join(sp, "README.md")):
                create_submodule_readme(mod, sub, info)
                sub_readme += 1
                sys.stdout.write("R")
            if not os.path.exists(os.path.join(sp, "AGENTS.md")):
                create_submodule_agents(mod, sub, info)
                sub_agents += 1
                sys.stdout.write("A")
            sys.stdout.flush()

    print(f"\n✅ Submodule README.md created: {sub_readme}")
    print(f"✅ Submodule AGENTS.md created: {sub_agents}")
    print(f"📊 Total: {title_fixed + spec_fixed + sub_readme + sub_agents} improvements")


if __name__ == "__main__":
    main()
