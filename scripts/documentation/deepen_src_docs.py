#!/usr/bin/env python3
"""Deepen src-level README.md quality by adding missing sections.

Adds:
1. ## Installation section (pip install codomyrmex)
2. ## Testing section (pytest command)
3. Deeper Quick Start code (usage example beyond just import)
4. Cross-link to docs/modules/ counterpart
5. Missing submodule SPEC.md files
"""
import ast
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "codomyrmex")
DOCS = os.path.join(REPO, "docs", "modules")


def get_module_exports(mod_path):
    """Get exported classes/functions from module."""
    init = os.path.join(mod_path, "__init__.py")
    classes, functions = [], []
    if not os.path.exists(init):
        return classes, functions
    try:
        tree = ast.parse(open(init).read())
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node) or ""
                classes.append((node.name, doc.split("\n")[0] if doc else ""))
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                doc = ast.get_docstring(node) or ""
                functions.append((node.name, doc.split("\n")[0] if doc else ""))
    except Exception:
        pass

    # Fallback: scan other .py files
    if not classes and not functions:
        seen_c, seen_f = set(), set()
        for f in sorted(os.listdir(mod_path)):
            if not f.endswith(".py") or f == "__init__.py":
                continue
            try:
                sub = ast.parse(open(os.path.join(mod_path, f)).read())
                for node in sub.body:
                    if isinstance(node, ast.ClassDef) and node.name not in seen_c:
                        doc = ast.get_docstring(node) or ""
                        classes.append((node.name, doc.split("\n")[0] if doc else ""))
                        seen_c.add(node.name)
                    elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_") and node.name not in seen_f:
                        doc = ast.get_docstring(node) or ""
                        functions.append((node.name, doc.split("\n")[0] if doc else ""))
                        seen_f.add(node.name)
            except Exception:
                pass
            if len(classes) >= 5:
                break

    return classes, functions


def build_usage_example(mod_name, classes, functions):
    """Build a realistic usage example with comments."""
    lines = []
    if classes and len(classes) >= 2:
        c1, c2 = classes[0], classes[1]
        lines.append(f"from codomyrmex.{mod_name} import {c1[0]}, {c2[0]}")
        lines.append("")
        lines.append(f"# Create a {c1[0]} instance")
        lines.append(f"{c1[0].lower()} = {c1[0]}()")
        lines.append("")
        lines.append(f"# Use {c2[0]} for additional functionality")
        lines.append(f"{c2[0].lower()} = {c2[0]}()")
    elif classes:
        c = classes[0]
        lines.append(f"from codomyrmex.{mod_name} import {c[0]}")
        lines.append("")
        lines.append(f"# Initialize and use {c[0]}")
        lines.append(f"{c[0].lower()} = {c[0]}()")
        if functions:
            fn = functions[0]
            lines.append(f"")
            lines.append(f"from codomyrmex.{mod_name} import {fn[0]}")
            lines.append(f"result = {fn[0]}()")
    elif functions and len(functions) >= 2:
        f1, f2 = functions[0], functions[1]
        lines.append(f"from codomyrmex.{mod_name} import {f1[0]}, {f2[0]}")
        lines.append("")
        lines.append(f"# {f1[1] or 'Call ' + f1[0]}")
        lines.append(f"result = {f1[0]}()")
        lines.append("")
        lines.append(f"# {f2[1] or 'Call ' + f2[0]}")
        lines.append(f"output = {f2[0]}()")
    elif functions:
        fn = functions[0]
        lines.append(f"from codomyrmex.{mod_name} import {fn[0]}")
        lines.append("")
        lines.append(f"# {fn[1] or 'Call ' + fn[0]}")
        lines.append(f"result = {fn[0]}()")
    else:
        lines.append(f"import codomyrmex.{mod_name}")
        lines.append("")
        lines.append(f"# Explore the {mod_name} module")
        lines.append(f"print(dir(codomyrmex.{mod_name}))")

    return lines


def deepen_readme(mod_name):
    """Add Installation, Testing, cross-links, and deeper Quick Start."""
    readme = os.path.join(SRC, mod_name, "README.md")
    if not os.path.exists(readme):
        return False

    with open(readme) as f:
        content = f.read()

    original = content
    content_lower = content.lower()

    # 1. Add Testing section if missing
    if "test" not in content_lower:
        testing = (
            f"\n## Testing\n\n"
            f"```bash\n"
            f"uv run python -m pytest src/codomyrmex/tests/ -k {mod_name} -v\n"
            f"```\n"
        )
        # Insert before Navigation section if it exists
        if "## Navigation" in content:
            content = content.replace("## Navigation", testing + "\n## Navigation")
        else:
            content = content.rstrip() + "\n" + testing

    # 2. Add Installation section if missing
    content_lower = content.lower()
    if "install" not in content_lower and "setup" not in content_lower and "pip" not in content_lower:
        install = (
            f"\n## Installation\n\n"
            f"```bash\n"
            f"pip install codomyrmex\n"
            f"```\n\n"
            f"Or for development:\n\n"
            f"```bash\n"
            f"uv sync\n"
            f"```\n"
        )
        # Insert after Overview/description, before Key Exports or Quick Start
        for anchor in ["## Key Export", "## Quick Start", "## Feature", "## Source", "## Testing", "## Navigation"]:
            if anchor in content:
                content = content.replace(anchor, install + "\n" + anchor)
                break
        else:
            content = content.rstrip() + "\n" + install

    # 3. Deepen Quick Start code if too short
    blocks = content.split("```")
    if len(blocks) >= 3:
        first_code = blocks[1]
        code_lines = [l for l in first_code.strip().split("\n") if l.strip() and not l.strip().startswith("#")]
        if len(code_lines) <= 3:
            classes, functions = get_module_exports(os.path.join(SRC, mod_name))
            if classes or functions:
                usage = build_usage_example(mod_name, classes, functions)
                lang_line = first_code.split("\n")[0] if first_code.strip() else "python"
                new_code = lang_line + "\n" + "\n".join(usage) + "\n"
                blocks[1] = new_code
                content = "```".join(blocks)

    # 4. Add cross-link to docs/modules
    if "docs/modules/" not in content and os.path.isdir(os.path.join(DOCS, mod_name)):
        cross = (
            f"\n## Documentation\n\n"
            f"- [Module Documentation](../../../docs/modules/{mod_name}/README.md)\n"
            f"- [Agent Guide](../../../docs/modules/{mod_name}/AGENTS.md)\n"
            f"- [Specification](../../../docs/modules/{mod_name}/SPEC.md)\n"
        )
        if "## Navigation" in content:
            content = content.replace("## Navigation", cross + "\n## Navigation")
        elif "## Testing" in content:
            content = content.replace("## Testing", cross + "\n## Testing")
        else:
            content = content.rstrip() + "\n" + cross

    if content != original:
        with open(readme, "w") as f:
            f.write(content)
        return True
    return False


def get_display_name(name):
    """Get display name for module."""
    display_map = {
        "api": "API", "cli": "CLI", "llm": "LLM", "ide": "IDE", "fpf": "FPF",
        "i18n": "i18n", "ci_cd_automation": "CI/CD Automation", "utils": "Utilities",
        "logging_monitoring": "Logging & Monitoring", "tree_sitter": "Tree-sitter",
        "auth": "Authentication", "dark": "Dark Modes", "cerebrum": "CEREBRUM",
        "graph_rag": "Graph RAG", "pdf": "PDF",
    }
    return display_map.get(name, name.replace("_", " ").title())


def create_submodule_spec(parent, sub):
    """Create SPEC.md for submodule."""
    spec_path = os.path.join(SRC, parent, sub, "SPEC.md")
    if os.path.exists(spec_path):
        return False

    display = get_display_name(sub)
    parent_display = get_display_name(parent)

    classes, functions = get_module_exports(os.path.join(SRC, parent, sub))

    # Get docstring
    init = os.path.join(SRC, parent, sub, "__init__.py")
    desc = f"{display} submodule."
    try:
        tree = ast.parse(open(init).read())
        if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
            desc = tree.body[0].value.value.strip().split("\n")[0]
    except Exception:
        pass

    content = f"# {display} — Functional Specification\n\n"
    content += f"**Module**: `codomyrmex.{parent}.{sub}`\n"
    content += f"**Status**: Active\n\n"
    content += f"## 1. Overview\n\n{desc}\n\n"
    content += f"## 2. Architecture\n\n"

    if classes:
        content += "### Components\n\n"
        content += "| Component | Type | Description |\n"
        content += "|-----------|------|-------------|\n"
        for name, doc in classes[:5]:
            content += f"| `{name}` | Class | {doc or name} |\n"
        content += "\n"

    content += f"## 3. API Usage\n\n```python\n"
    if classes:
        content += f"from codomyrmex.{parent}.{sub} import {classes[0][0]}\n"
    elif functions:
        content += f"from codomyrmex.{parent}.{sub} import {functions[0][0]}\n"
    else:
        content += f"import codomyrmex.{parent}.{sub}\n"
    content += "```\n\n"

    content += "## 4. Dependencies\n\n"
    content += f"See `src/codomyrmex/{parent}/{sub}/__init__.py` for import dependencies.\n\n"

    content += "## 5. Testing\n\n```bash\n"
    content += f"uv run python -m pytest src/codomyrmex/tests/ -k {sub} -v\n"
    content += "```\n\n"

    content += "## References\n\n"
    content += f"- [README.md](README.md)\n"
    content += f"- [AGENTS.md](AGENTS.md)\n"
    content += f"- [Parent: {parent_display}](../SPEC.md)\n"

    with open(spec_path, "w") as f:
        f.write(content)
    return True


def main():
    modules = sorted(
        d for d in os.listdir(SRC)
        if os.path.isdir(os.path.join(SRC, d)) and d != "__pycache__"
    )

    # Phase 1: Deepen READMEs
    readme_improved = 0
    for mod in modules:
        if deepen_readme(mod):
            readme_improved += 1
            sys.stdout.write("R")
        else:
            sys.stdout.write(".")
        sys.stdout.flush()
    print(f"\n✅ README.md deepened: {readme_improved}")

    # Phase 2: Create missing submodule SPEC.md
    spec_created = 0
    for mod in modules:
        mod_path = os.path.join(SRC, mod)
        for sub in sorted(os.listdir(mod_path)):
            sp = os.path.join(mod_path, sub)
            if not os.path.isdir(sp) or sub == "__pycache__":
                continue
            if not os.path.exists(os.path.join(sp, "__init__.py")):
                continue
            if create_submodule_spec(mod, sub):
                spec_created += 1
                sys.stdout.write("S")
                sys.stdout.flush()

    print(f"\n✅ Submodule SPEC.md created: {spec_created}")
    print(f"📊 Total: {readme_improved + spec_created} improvements")


if __name__ == "__main__":
    main()
