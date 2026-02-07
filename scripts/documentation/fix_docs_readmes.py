#!/usr/bin/env python3
"""Add Testing, Installation, and code blocks to remaining docs/modules READMEs and SPECs."""
import ast
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "codomyrmex")
DOCS = os.path.join(REPO, "docs", "modules")


def get_exports(mod_name):
    """Get classes and functions from src."""
    init = os.path.join(SRC, mod_name, "__init__.py")
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
    if not classes and not functions:
        for f in sorted(os.listdir(os.path.join(SRC, mod_name))):
            if not f.endswith(".py") or f == "__init__.py": continue
            try:
                sub = ast.parse(open(os.path.join(SRC, mod_name, f)).read())
                for node in sub.body:
                    if isinstance(node, ast.ClassDef):
                        doc = ast.get_docstring(node) or ""
                        classes.append((node.name, doc.split("\n")[0] if doc else ""))
                    elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                        doc = ast.get_docstring(node) or ""
                        functions.append((node.name, doc.split("\n")[0] if doc else ""))
            except Exception:
                pass
            if len(classes) >= 3: break
    return classes, functions


def fix_readme(mod_name):
    """Add missing sections to docs/modules README."""
    readme = os.path.join(DOCS, mod_name, "README.md")
    if not os.path.exists(readme):
        return False
    with open(readme) as f:
        content = f.read()
    original = content
    classes, functions = get_exports(mod_name)

    # Add Installation
    if "install" not in content.lower() and "pip" not in content.lower() and "setup" not in content.lower():
        install = "\n## Installation\n\n```bash\npip install codomyrmex\n```\n"
        for anchor in ["## API", "## Key", "## Quick", "## Test", "## Related", "## Navigation", "## References"]:
            if anchor in content:
                content = content.replace(anchor, install + "\n" + anchor)
                break
        else:
            content = content.rstrip() + "\n" + install

    # Add Testing
    if "test" not in content.lower():
        testing = f"\n## Testing\n\n```bash\nuv run python -m pytest src/codomyrmex/tests/ -k {mod_name} -v\n```\n"
        for anchor in ["## Related", "## Navigation", "## References"]:
            if anchor in content:
                content = content.replace(anchor, testing + "\n" + anchor)
                break
        else:
            content = content.rstrip() + "\n" + testing

    # Add code block if missing
    if "```" not in content:
        code = "\n## Quick Start\n\n```python\n"
        if classes:
            code += f"from codomyrmex.{mod_name} import {classes[0][0]}\n\n"
            code += f"{classes[0][0].lower()} = {classes[0][0]}()\n"
        elif functions:
            code += f"from codomyrmex.{mod_name} import {functions[0][0]}\n\n"
            code += f"result = {functions[0][0]}()\n"
        else:
            code += f"import codomyrmex.{mod_name}\n"
        code += "```\n"
        for anchor in ["## Test", "## Related", "## Navigation", "## References"]:
            if anchor in content:
                content = content.replace(anchor, code + "\n" + anchor)
                break
        else:
            content = content.rstrip() + "\n" + code

    if content != original:
        with open(readme, "w") as f:
            f.write(content)
        return True
    return False


def fix_spec(mod_name):
    """Add code block to docs/modules SPEC if missing."""
    spec = os.path.join(DOCS, mod_name, "SPEC.md")
    if not os.path.exists(spec):
        return False
    with open(spec) as f:
        content = f.read()
    if "```" in content:
        return False
    classes, functions = get_exports(mod_name)
    code = "\n## API Usage\n\n```python\n"
    if classes:
        code += f"from codomyrmex.{mod_name} import {classes[0][0]}\n"
    elif functions:
        code += f"from codomyrmex.{mod_name} import {functions[0][0]}\n"
    else:
        code += f"import codomyrmex.{mod_name}\n"
    code += "```\n"
    content = content.rstrip() + "\n" + code
    with open(spec, "w") as f:
        f.write(content)
    return True


def main():
    modules = sorted(d for d in os.listdir(DOCS) if os.path.isdir(os.path.join(DOCS, d)))
    readme_fixed = spec_fixed = 0
    for mod in modules:
        if fix_readme(mod):
            readme_fixed += 1
            sys.stdout.write("R")
        else:
            sys.stdout.write(".")
        sys.stdout.flush()
    print(f"\n✅ docs README.md fixed: {readme_fixed}")
    for mod in modules:
        if fix_spec(mod):
            spec_fixed += 1
            sys.stdout.write("S")
        else:
            sys.stdout.write(".")
        sys.stdout.flush()
    print(f"\n✅ docs SPEC.md fixed: {spec_fixed}")
    print(f"📊 Total: {readme_fixed + spec_fixed}")


if __name__ == "__main__":
    main()
