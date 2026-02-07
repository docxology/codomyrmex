#!/usr/bin/env python3
"""Enrich docs/modules AGENTS.md and README.md files.

1. Add testing sections to AGENTS.md (84 missing)
2. Add code examples to AGENTS.md (2 missing)
3. Deepen thin AGENTS.md files (61 under 30 lines)
4. Deepen thin README.md files (20 under 40 lines)
5. Deepen thin SPEC.md (2 under 35 lines)
"""
import ast
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "codomyrmex")
DOCS = os.path.join(REPO, "docs", "modules")

DISPLAY_MAP = {
    "api": "API", "cli": "CLI", "llm": "LLM", "ide": "IDE", "fpf": "FPF",
    "i18n": "i18n", "ci_cd_automation": "CI/CD Automation", "utils": "Utilities",
    "logging_monitoring": "Logging & Monitoring", "tree_sitter": "Tree-sitter",
    "auth": "Authentication", "dark": "Dark Modes", "cerebrum": "CEREBRUM",
    "graph_rag": "Graph RAG",
}


def get_display(name):
    return DISPLAY_MAP.get(name, name.replace("_", " ").title())


def get_exports(mod_name):
    """Get classes and functions from src's __init__.py."""
    init = os.path.join(SRC, mod_name, "__init__.py")
    classes, functions = [], []
    if not os.path.exists(init):
        return classes, functions
    try:
        tree = ast.parse(open(init).read())
        seen_c, seen_f = set(), set()
        for node in tree.body:
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

    # Fallback: scan .py files
    if not classes and not functions:
        seen_c, seen_f = set(), set()
        for f in sorted(os.listdir(os.path.join(SRC, mod_name))):
            if not f.endswith(".py") or f == "__init__.py":
                continue
            try:
                sub = ast.parse(open(os.path.join(SRC, mod_name, f)).read())
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


def get_submodules(mod_name):
    """Get submodule names."""
    p = os.path.join(SRC, mod_name)
    subs = []
    for d in sorted(os.listdir(p)):
        sp = os.path.join(p, d)
        if os.path.isdir(sp) and d != "__pycache__" and os.path.exists(os.path.join(sp, "__init__.py")):
            subs.append(d)
    return subs


def enrich_docs_agents(mod_name):
    """Enrich docs/modules AGENTS.md."""
    agents = os.path.join(DOCS, mod_name, "AGENTS.md")
    if not os.path.exists(agents):
        return False

    with open(agents) as f:
        content = f.read()

    original = content
    content_lower = content.lower()
    classes, functions = get_exports(mod_name)
    display = get_display(mod_name)
    subs = get_submodules(mod_name)

    # Add testing section if missing
    if "test" not in content_lower:
        testing = (
            f"\n## Testing Guidelines\n\n"
            f"```bash\n"
            f"uv run python -m pytest src/codomyrmex/tests/ -k {mod_name} -v\n"
            f"```\n\n"
            f"- Run tests before and after making changes.\n"
            f"- Ensure all existing tests pass before submitting.\n"
        )
        if "## Navigation" in content:
            content = content.replace("## Navigation", testing + "\n## Navigation")
        else:
            content = content.rstrip() + "\n" + testing

    # Add code examples if missing
    if "```" not in content:
        code = f"\n## Common Patterns\n\n```python\n"
        if classes:
            imports = ", ".join(c[0] for c in classes[:3])
            code += f"from codomyrmex.{mod_name} import {imports}\n\n"
            code += f"# Initialize {classes[0][0]}\n"
            code += f"{classes[0][0].lower()} = {classes[0][0]}()\n"
        elif functions:
            imports = ", ".join(fn[0] for fn in functions[:3])
            code += f"from codomyrmex.{mod_name} import {imports}\n\n"
            code += f"# {functions[0][1] or 'Call ' + functions[0][0]}\n"
            code += f"result = {functions[0][0]}()\n"
        else:
            code += f"import codomyrmex.{mod_name}\n"
        code += "```\n"
        if "## Testing" in content:
            content = content.replace("## Testing", code + "\n## Testing")
        else:
            content = content.rstrip() + "\n" + code

    # Add key components if thin (under 30 lines)
    if sum(1 for _ in content.split("\n")) < 35 and (classes or functions or subs):
        components = f"\n## Key Components\n\n"
        if classes:
            for name, doc in classes[:5]:
                components += f"- **`{name}`** — {doc or name}\n"
        if functions:
            for name, doc in functions[:5]:
                components += f"- **`{name}()`** — {doc or name}\n"
        if subs:
            components += f"\n### Submodules\n\n"
            for sub in subs[:8]:
                components += f"- `{sub}` — {get_display(sub)}\n"
        components += "\n"

        # Insert after overview or description
        for anchor in ["## Common Patterns", "## Testing", "## Navigation"]:
            if anchor in content:
                content = content.replace(anchor, components + anchor)
                break
        else:
            content = content.rstrip() + "\n" + components

    if content != original:
        with open(agents, "w") as f:
            f.write(content)
        return True
    return False


def enrich_docs_readme(mod_name):
    """Enrich thin docs/modules README.md."""
    readme = os.path.join(DOCS, mod_name, "README.md")
    if not os.path.exists(readme):
        return False

    with open(readme) as f:
        content = f.read()

    lc = sum(1 for _ in content.split("\n"))
    if lc >= 40:
        return False

    original = content
    classes, functions = get_exports(mod_name)
    subs = get_submodules(mod_name)

    # Add Installation if missing
    if "install" not in content.lower() and "pip" not in content.lower():
        install = (
            "\n## Installation\n\n```bash\npip install codomyrmex\n```\n"
        )
        for anchor in ["## API", "## Key", "## Quick", "## Testing", "## Navigation"]:
            if anchor in content:
                content = content.replace(anchor, install + "\n" + anchor)
                break
        else:
            content = content.rstrip() + "\n" + install

    # Add Quick Start if missing code blocks
    if "```" not in content:
        code = f"\n## Quick Start\n\n```python\n"
        if classes:
            code += f"from codomyrmex.{mod_name} import {classes[0][0]}\n\n"
            code += f"{classes[0][0].lower()} = {classes[0][0]}()\n"
        elif functions:
            code += f"from codomyrmex.{mod_name} import {functions[0][0]}\n\n"
            code += f"result = {functions[0][0]}()\n"
        else:
            code += f"import codomyrmex.{mod_name}\n"
        code += "```\n"
        content = content.rstrip() + "\n" + code

    # Add Testing if missing
    if "test" not in content.lower():
        testing = (
            f"\n## Testing\n\n```bash\n"
            f"uv run python -m pytest src/codomyrmex/tests/ -k {mod_name} -v\n"
            f"```\n"
        )
        content = content.rstrip() + "\n" + testing

    # Add submodule listing if present
    if subs and "submodule" not in content.lower() and "sub-module" not in content.lower():
        sub_section = "\n## Submodules\n\n"
        for sub in subs[:10]:
            sub_section += f"- **`{sub}`** — {get_display(sub)}\n"
        sub_section += "\n"
        for anchor in ["## Testing", "## Navigation"]:
            if anchor in content:
                content = content.replace(anchor, sub_section + anchor)
                break
        else:
            content = content.rstrip() + "\n" + sub_section

    if content != original:
        with open(readme, "w") as f:
            f.write(content)
        return True
    return False


def enrich_docs_spec(mod_name):
    """Enrich thin docs/modules SPEC.md."""
    spec = os.path.join(DOCS, mod_name, "SPEC.md")
    if not os.path.exists(spec):
        return False

    with open(spec) as f:
        content = f.read()

    lc = sum(1 for _ in content.split("\n"))
    if lc >= 35:
        return False

    original = content
    classes, functions = get_exports(mod_name)

    # Add code block if missing
    if "```" not in content:
        code = f"\n## API Usage\n\n```python\n"
        if classes:
            code += f"from codomyrmex.{mod_name} import {classes[0][0]}\n"
        elif functions:
            code += f"from codomyrmex.{mod_name} import {functions[0][0]}\n"
        else:
            code += f"import codomyrmex.{mod_name}\n"
        code += "```\n"
        content = content.rstrip() + "\n" + code

    # Add testing if missing
    if "test" not in content.lower():
        testing = (
            f"\n## Testing\n\n```bash\n"
            f"uv run python -m pytest src/codomyrmex/tests/ -k {mod_name} -v\n"
            f"```\n"
        )
        content = content.rstrip() + "\n" + testing

    if content != original:
        with open(spec, "w") as f:
            f.write(content)
        return True
    return False


def main():
    modules = sorted(
        d for d in os.listdir(DOCS)
        if os.path.isdir(os.path.join(DOCS, d))
    )

    agents_improved = 0
    readme_improved = 0
    spec_improved = 0

    for mod in modules:
        if enrich_docs_agents(mod):
            agents_improved += 1
            sys.stdout.write("A")
        else:
            sys.stdout.write(".")
        sys.stdout.flush()
    print(f"\n✅ docs AGENTS.md enriched: {agents_improved}")

    for mod in modules:
        if enrich_docs_readme(mod):
            readme_improved += 1
            sys.stdout.write("R")
        else:
            sys.stdout.write(".")
        sys.stdout.flush()
    print(f"\n✅ docs README.md enriched: {readme_improved}")

    for mod in modules:
        if enrich_docs_spec(mod):
            spec_improved += 1
            sys.stdout.write("S")
        else:
            sys.stdout.write(".")
        sys.stdout.flush()
    print(f"\n✅ docs SPEC.md enriched: {spec_improved}")

    print(f"📊 Total: {agents_improved + readme_improved + spec_improved} improvements")


if __name__ == "__main__":
    main()
