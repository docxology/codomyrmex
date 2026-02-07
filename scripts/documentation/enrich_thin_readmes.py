#!/usr/bin/env python3
"""Enrich the 17 remaining thin README files by reading deeper into module structure."""
import ast
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = os.path.join(REPO, "docs", "modules")
SRC = os.path.join(REPO, "src", "codomyrmex")

DISPLAY = {
    "build_synthesis": "Build Synthesis", "ci_cd_automation": "CI/CD Automation",
    "config_management": "Config Management", "defense": "Defense",
    "environment_setup": "Environment Setup", "examples": "Examples",
    "identity": "Identity", "logging_monitoring": "Logging & Monitoring",
    "market": "Market", "module_template": "Module Template",
    "pattern_matching": "Pattern Matching", "physical_management": "Physical Management",
    "plugin_system": "Plugin System", "privacy": "Privacy",
    "system_discovery": "System Discovery", "tools": "Tools", "website": "Website",
}

# For modules whose __init__.py docstring is too generic, provide curated descriptions
DESCRIPTIONS = {
    "build_synthesis": "Automated build pipeline synthesis including dependency resolution, compilation orchestration, and artifact generation.",
    "ci_cd_automation": "CI/CD pipeline automation with GitHub Actions, GitLab CI, and Jenkins integration support.",
    "config_management": "Hierarchical configuration management with environment-aware overrides, validation, and hot-reloading.",
    "defense": "Active countermeasures and containment strategies including rabbit hole detection, sandboxing, and threat response.",
    "environment_setup": "Automated development environment provisioning with Python, Node.js, and system dependency management.",
    "examples": "Reference implementations and demonstrations showcasing Codomyrmex module integration patterns.",
    "identity": "Persona management and bio-cognitive verification for agent identity and authentication.",
    "logging_monitoring": "Structured logging, metric collection, and system monitoring with pluggable backends.",
    "market": "Reverse auction and demand aggregation capabilities for resource allocation and pricing.",
    "module_template": "Template for creating new Codomyrmex modules with standard structure, testing, and documentation.",
    "pattern_matching": "Advanced pattern matching with regex, glob, AST, and structural pattern support.",
    "physical_management": "Physical object management, simulation, and tracking with spatial awareness.",
    "plugin_system": "Dynamic plugin loading, discovery, and lifecycle management with sandboxed execution.",
    "privacy": "Data sanitization via crumb cleaning and anonymous routing via mixnet patterns.",
    "system_discovery": "Automatic system capability detection, dependency resolution, and environment profiling.",
    "tools": "Tool calling framework with registration, validation, execution, and composable tool chains.",
    "website": "Website generation, static site building, and web content management utilities.",
}


def get_py_files(mod):
    """Get all .py file names in a module directory."""
    mod_dir = os.path.join(SRC, mod)
    return sorted(f for f in os.listdir(mod_dir) if f.endswith(".py") and f != "__init__.py")


def get_submodules(mod):
    """Get submodule directories."""
    mod_dir = os.path.join(SRC, mod)
    subs = []
    for child in sorted(os.listdir(mod_dir)):
        child_path = os.path.join(mod_dir, child)
        if os.path.isdir(child_path) and os.path.exists(os.path.join(child_path, "__init__.py")):
            sub_doc = ""
            try:
                tree = ast.parse(open(os.path.join(child_path, "__init__.py")).read())
                if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
                    sub_doc = tree.body[0].value.value.strip().split("\n")[0]
            except Exception:
                pass
            subs.append((child, sub_doc or child.replace("_", " ").title()))
    return subs


def get_classes_from_files(mod):
    """Get classes from .py files in the module (not just __init__.py)."""
    mod_dir = os.path.join(SRC, mod)
    classes = []
    seen = set()
    for f in sorted(os.listdir(mod_dir)):
        if not f.endswith(".py") or f == "__init__.py":
            continue
        try:
            tree = ast.parse(open(os.path.join(mod_dir, f)).read())
            for node in tree.body:
                if isinstance(node, ast.ClassDef) and node.name not in seen:
                    doc = ast.get_docstring(node) or ""
                    classes.append((node.name, doc.split("\n")[0] if doc else "", f))
                    seen.add(node.name)
        except Exception:
            pass
    return classes[:12]  # Limit


def get_functions_from_files(mod):
    """Get top-level functions from .py files."""
    mod_dir = os.path.join(SRC, mod)
    funcs = []
    seen = set()
    for f in sorted(os.listdir(mod_dir)):
        if not f.endswith(".py") or f == "__init__.py":
            continue
        try:
            tree = ast.parse(open(os.path.join(mod_dir, f)).read())
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and not node.name.startswith("_") and node.name not in seen:
                    doc = ast.get_docstring(node) or ""
                    funcs.append((node.name, doc.split("\n")[0] if doc else ""))
                    seen.add(node.name)
        except Exception:
            pass
    return funcs[:8]


def get_version(mod):
    init = os.path.join(SRC, mod, "__init__.py")
    if not os.path.exists(init):
        return "0.1.0"
    try:
        tree = ast.parse(open(init).read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__version__" and isinstance(node.value, ast.Constant):
                        return str(node.value.value)
    except Exception:
        pass
    return "0.1.0"


def main():
    thin_mods = []
    for d in sorted(os.listdir(DOCS)):
        readme = os.path.join(DOCS, d, "README.md")
        if not os.path.isfile(readme):
            continue
        with open(readme) as f:
            lc = sum(1 for _ in f)
        if lc < 30:
            thin_mods.append(d)
    
    print(f"Found {len(thin_mods)} thin README files to enrich")
    
    fixed = 0
    for mod in thin_mods:
        display = DISPLAY.get(mod, mod.replace("_", " ").title())
        desc = DESCRIPTIONS.get(mod, f"{display} module for Codomyrmex.")
        version = get_version(mod)
        py_files = get_py_files(mod)
        submodules = get_submodules(mod)
        classes = get_classes_from_files(mod)
        functions = get_functions_from_files(mod)
        
        lines = [
            f"# {display} Module Documentation",
            "",
            f"**Version**: v{version} | **Status**: Active | **Last Updated**: February 2026",
            "",
            "## Overview",
            "",
            desc,
            "",
        ]
        
        # Key Features from classes + functions
        features = []
        for name, doc, _ in classes[:6]:
            features.append(f"- **{name}** — {doc or name}")
        for name, doc in functions[:4]:
            features.append(f"- `{name}()` — {doc or name}")
        
        if features:
            lines.append("## Key Features")
            lines.append("")
            lines.extend(features)
            lines.append("")
        
        # Submodules
        if submodules:
            lines.append("## Submodules")
            lines.append("")
            lines.append("| Submodule | Description |")
            lines.append("|-----------|-------------|")
            for name, doc in submodules:
                lines.append(f"| `{name}` | {doc} |")
            lines.append("")
        
        # Quick Start
        lines.append("## Quick Start")
        lines.append("")
        lines.append("```python")
        if classes:
            imports = ", ".join(c[0] for c in classes[:3])
            lines.append(f"from codomyrmex.{mod} import {imports}")
            lines.append("")
            lines.append(f"instance = {classes[0][0]}()")
        elif functions:
            imports = ", ".join(f[0] for f in functions[:3])
            lines.append(f"from codomyrmex.{mod} import {imports}")
            lines.append("")
            lines.append(f"result = {functions[0][0]}()")
        else:
            lines.append(f"from codomyrmex.{mod} import *")
            lines.append("")
            lines.append(f"# See source module for available APIs")
        lines.append("```")
        lines.append("")
        
        # Source Structure
        if py_files:
            lines.append("## Source Files")
            lines.append("")
            for f in py_files[:8]:
                lines.append(f"- `{f}`")
            if len(py_files) > 8:
                lines.append(f"- ...and {len(py_files) - 8} more")
            lines.append("")
        
        # Directory Contents
        lines.append("## Directory Contents")
        lines.append("")
        lines.append("| File | Description |")
        lines.append("|------|-------------|")
        lines.append("| `README.md` | This documentation |")
        lines.append("| `AGENTS.md` | Agent coordination guide |")
        lines.append("| `SPEC.md` | Technical specification |")
        docs_dir = os.path.join(DOCS, mod)
        for child in sorted(os.listdir(docs_dir)):
            if os.path.isdir(os.path.join(docs_dir, child)):
                lines.append(f"| `{child}/` | {child.replace('_', ' ').title()} |")
        lines.append("")
        
        # Navigation
        lines.append("## Navigation")
        lines.append("")
        lines.append(f"- **Source**: [src/codomyrmex/{mod}/](../../../src/codomyrmex/{mod}/)")
        lines.append("- **Parent**: [Modules](../README.md)")
        lines.append("")
        
        readme_path = os.path.join(DOCS, mod, "README.md")
        with open(readme_path, "w") as f:
            f.write("\n".join(lines))
        fixed += 1
        print(f"  ✅ {mod}/README.md ({len(lines)} lines)")
    
    print(f"\n✅ Enriched {fixed} README files")


if __name__ == "__main__":
    main()
