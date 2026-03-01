#!/usr/bin/env python3
"""Enrich src-level README.md and AGENTS.md with code blocks and feature sections.

Reads __init__.py via AST to extract classes, functions, submodules.
Injects missing sections: Quick Start, Key Exports, code examples.
Preserves existing content — only appends/inserts missing sections.
"""
import ast
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "codomyrmex")


def get_module_info(mod_name):
    """Extract module info from __init__.py."""
    init = os.path.join(SRC, mod_name, "__init__.py")
    info = {"classes": [], "functions": [], "submodules": [], "version": "0.1.0", "desc": ""}
    if not os.path.exists(init):
        return info
    try:
        content = open(init).read()
        tree = ast.parse(content)
    except Exception:
        return info

    # Module docstring
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
        info["desc"] = tree.body[0].value.value.strip().split("\n")[0]

    # Top-level classes and functions only
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
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__version__" and isinstance(node.value, ast.Constant):
                    info["version"] = str(node.value.value)

    # Also scan .py files for top-level classes/functions if __init__.py had none
    if not info["classes"] and not info["functions"]:
        mod_dir = os.path.join(SRC, mod_name)
        for f in sorted(os.listdir(mod_dir)):
            if not f.endswith(".py") or f == "__init__.py":
                continue
            try:
                sub_tree = ast.parse(open(os.path.join(mod_dir, f)).read())
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
            if len(info["classes"]) >= 8 or len(info["functions"]) >= 8:
                break

    # Submodules
    mod_dir = os.path.join(SRC, mod_name)
    for child in sorted(os.listdir(mod_dir)):
        child_path = os.path.join(mod_dir, child)
        if os.path.isdir(child_path) and os.path.exists(os.path.join(child_path, "__init__.py")) and child != "__pycache__":
            sub_doc = ""
            try:
                sub_tree = ast.parse(open(os.path.join(child_path, "__init__.py")).read())
                if sub_tree.body and isinstance(sub_tree.body[0], ast.Expr) and isinstance(sub_tree.body[0].value, ast.Constant):
                    sub_doc = sub_tree.body[0].value.value.strip().split("\n")[0]
            except Exception:
                pass
            info["submodules"].append((child, sub_doc or child.replace("_", " ").title()))

    return info


def build_quick_start(mod_name, info):
    """Build a Quick Start code block."""
    lines = ["## Quick Start", "", "```python"]
    if info["classes"]:
        imports = ", ".join(c[0] for c in info["classes"][:3])
        lines.append(f"from codomyrmex.{mod_name} import {imports}")
        lines.append("")
        cls = info["classes"][0][0]
        lines.append(f"# Initialize {cls}")
        lines.append(f"instance = {cls}()")
    elif info["functions"]:
        imports = ", ".join(f[0] for f in info["functions"][:3])
        lines.append(f"from codomyrmex.{mod_name} import {imports}")
        lines.append("")
        fn = info["functions"][0][0]
        lines.append(f"result = {fn}()")
    else:
        lines.append(f"import codomyrmex.{mod_name}")
    lines.extend(["```", ""])
    return "\n".join(lines)


def build_key_exports(mod_name, info):
    """Build a Key Exports section."""
    lines = ["## Key Exports", ""]
    if info["classes"]:
        lines.append("### Classes")
        for name, doc in info["classes"][:8]:
            lines.append(f"- **`{name}`** — {doc or name}")
        lines.append("")
    if info["functions"]:
        lines.append("### Functions")
        for name, doc in info["functions"][:8]:
            lines.append(f"- **`{name}()`** — {doc or name}")
        lines.append("")
    if info["submodules"]:
        lines.append("### Submodules")
        for name, doc in info["submodules"][:10]:
            lines.append(f"- **`{name}/`** — {doc}")
        lines.append("")
    return "\n".join(lines)


def build_agents_code(mod_name, info):
    """Build a code example block for AGENTS.md."""
    lines = ["## Common Patterns", "", "```python"]
    if info["classes"]:
        imports = ", ".join(c[0] for c in info["classes"][:3])
        lines.append(f"from codomyrmex.{mod_name} import {imports}")
        lines.append("")
        cls = info["classes"][0][0]
        lines.append(f"# Agent uses {cls}")
        lines.append(f"instance = {cls}()")
    elif info["functions"]:
        imports = ", ".join(f[0] for f in info["functions"][:3])
        lines.append(f"from codomyrmex.{mod_name} import {imports}")
        lines.append("")
        fn = info["functions"][0][0]
        lines.append(f"result = {fn}()")
    else:
        lines.append(f"import codomyrmex.{mod_name}")
        lines.append("")
        lines.append(f"# Agent interacts with {mod_name}")
    lines.extend(["```", ""])
    return "\n".join(lines)


def enrich_readme(mod_name, info):
    """Add missing sections to src README.md."""
    readme_path = os.path.join(SRC, mod_name, "README.md")
    with open(readme_path) as f:
        content = f.read()

    modified = False

    # Add Quick Start if no code blocks exist
    if "```" not in content:
        qs = build_quick_start(mod_name, info)
        # Insert before Navigation Links / Directory Structure or at end
        if "## Navigation" in content:
            content = content.replace("## Navigation", qs + "\n## Navigation")
        elif "## Directory" in content:
            content = content.replace("## Directory", qs + "\n## Directory")
        else:
            content = content.rstrip() + "\n\n" + qs
        modified = True

    # Add Key Exports if no features/exports section
    content_lower = content.lower()
    has_features = any(kw in content_lower for kw in [
        "key export", "features", "key class", "api reference",
        "directory structure", "component", "key function",
    ])
    if not has_features and (info["classes"] or info["functions"] or info["submodules"]):
        ke = build_key_exports(mod_name, info)
        # Insert after description / Overview section, before Quick Start
        if "## Quick Start" in content:
            content = content.replace("## Quick Start", ke + "\n## Quick Start")
        elif "```" in content:
            # Find the first code block and insert before it
            idx = content.index("```")
            # Find the section header before the code block
            last_heading = content.rfind("\n##", 0, idx)
            if last_heading > 0:
                content = content[:last_heading] + "\n" + ke + content[last_heading:]
            else:
                content = content.rstrip() + "\n\n" + ke
        else:
            content = content.rstrip() + "\n\n" + ke
        modified = True

    if modified:
        with open(readme_path, "w") as f:
            f.write(content)

    return modified


def enrich_agents(mod_name, info):
    """Add code examples to AGENTS.md if missing."""
    agents_path = os.path.join(SRC, mod_name, "AGENTS.md")
    with open(agents_path) as f:
        content = f.read()

    if "```" in content:
        return False

    code = build_agents_code(mod_name, info)
    # Insert before Navigation Links or at end
    if "## Navigation" in content:
        content = content.replace("## Navigation", code + "\n## Navigation")
    else:
        content = content.rstrip() + "\n\n" + code

    with open(agents_path, "w") as f:
        f.write(content)
    return True


def main():
    modules = sorted(
        d for d in os.listdir(SRC)
        if os.path.isdir(os.path.join(SRC, d)) and d != "__pycache__"
    )

    readme_fixed = 0
    agents_fixed = 0

    for mod in modules:
        info = get_module_info(mod)

        # Enrich README
        if enrich_readme(mod, info):
            readme_fixed += 1
            sys.stdout.write("R")
        else:
            sys.stdout.write(".")

        # Enrich AGENTS
        if enrich_agents(mod, info):
            agents_fixed += 1
            sys.stdout.write("A")

        sys.stdout.flush()

    print()
    print(f"✅ README.md enriched: {readme_fixed}")
    print(f"✅ AGENTS.md enriched: {agents_fixed}")
    print(f"📊 Total: {readme_fixed + agents_fixed} files improved")


if __name__ == "__main__":
    main()
