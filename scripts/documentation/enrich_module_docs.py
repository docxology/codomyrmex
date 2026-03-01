#!/usr/bin/env python3
"""
Enrich module documentation by reading source code structure.

Reads each src/codomyrmex/<module>/ directory and generates enriched
README.md, AGENTS.md, and SPEC.md files in docs/modules/<module>/.
"""

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "codomyrmex"
DOCS_ROOT = REPO_ROOT / "docs" / "modules"

# Human-readable display names for modules
DISPLAY_NAMES = {
    "accessibility": "Accessibility",
    "agentic_memory": "Agentic Memory",
    "agents": "AI Agents",
    "api": "API",
    "audio": "Audio Processing",
    "auth": "Authentication",
    "build_synthesis": "Build Synthesis",
    "cache": "Cache",
    "cerebrum": "Cerebrum",
    "chaos_engineering": "Chaos Engineering",
    "ci_cd_automation": "CI/CD Automation",
    "cli": "CLI",
    "cloud": "Cloud",
    "coding": "Coding",
    "collaboration": "Collaboration",
    "compression": "Compression",
    "concurrency": "Concurrency",
    "config_management": "Config Management",
    "containerization": "Containerization",
    "cost_management": "Cost Management",
    "dark": "Dark",
    "data_lineage": "Data Lineage",
    "data_visualization": "Data Visualization",
    "database_management": "Database Management",
    "defense": "Defense",
    "deployment": "Deployment",
    "documentation": "Documentation",
    "documents": "Documents",
    "edge_computing": "Edge Computing",
    "embodiment": "Embodiment",
    "encryption": "Encryption",
    "environment_setup": "Environment Setup",
    "events": "Events",
    "evolutionary_ai": "Evolutionary AI",
    "examples": "Examples",
    "feature_flags": "Feature Flags",
    "feature_store": "Feature Store",
    "fpf": "FPF (Filesystem Processing Framework)",
    "git_operations": "Git Operations",
    "graph_rag": "Graph RAG",
    "i18n": "Internationalization (i18n)",
    "ide": "IDE Integration",
    "identity": "Identity",
    "inference_optimization": "Inference Optimization",
    "llm": "LLM",
    "logging_monitoring": "Logging & Monitoring",
    "logistics": "Logistics",
    "market": "Market",
    "metrics": "Metrics",
    "migration": "Migration",
    "model_context_protocol": "Model Context Protocol",
    "model_ops": "Model Ops",
    "model_registry": "Model Registry",
    "module_template": "Module Template",
    "multimodal": "Multimodal",
    "networking": "Networking",
    "notification": "Notification",
    "observability_dashboard": "Observability Dashboard",
    "orchestrator": "Orchestrator",
    "pattern_matching": "Pattern Matching",
    "performance": "Performance",
    "physical_management": "Physical Management",
    "plugin_system": "Plugin System",
    "privacy": "Privacy",
    "prompt_testing": "Prompt Testing",
    "quantum": "Quantum",
    "rate_limiting": "Rate Limiting",
    "scheduler": "Scheduler",
    "scrape": "Scrape",
    "search": "Search",
    "security": "Security",
    "serialization": "Serialization",
    "service_mesh": "Service Mesh",
    "skills": "Skills",
    "smart_contracts": "Smart Contracts",
    "spatial": "Spatial",
    "static_analysis": "Static Analysis",
    "streaming": "Streaming",
    "system_discovery": "System Discovery",
    "telemetry": "Telemetry",
    "templating": "Templating",
    "terminal_interface": "Terminal Interface",
    "testing": "Testing",
    "tests": "Tests",
    "tools": "Tools",
    "tree_sitter": "Tree-sitter",
    "utils": "Utilities",
    "validation": "Validation",
    "vector_store": "Vector Store",
    "video": "Video",
    "wallet": "Wallet",
    "website": "Website",
    "workflow_testing": "Workflow Testing",
}


def extract_module_info(module_dir: Path) -> dict:
    """Extract information from a source module directory."""
    info = {
        "name": module_dir.name,
        "display_name": DISPLAY_NAMES.get(module_dir.name, module_dir.name.replace("_", " ").title()),
        "docstring": "",
        "classes": [],
        "functions": [],
        "submodules": [],
        "py_files": [],
        "has_tests": False,
        "version": "0.1.0",
    }
    
    init_file = module_dir / "__init__.py"
    if init_file.exists():
        content = init_file.read_text()
        try:
            tree = ast.parse(content)
            # Extract module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) 
                    and isinstance(tree.body[0].value, (ast.Constant, ast.Str))):
                raw = tree.body[0].value.value if isinstance(tree.body[0].value, ast.Constant) else tree.body[0].value.s
                info["docstring"] = raw.strip()
            
            # Extract classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    doc = ast.get_docstring(node) or ""
                    info["classes"].append({
                        "name": node.name,
                        "doc": doc.split("\n")[0] if doc else "",
                    })
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):
                        doc = ast.get_docstring(node) or ""
                        info["functions"].append({
                            "name": node.name,
                            "doc": doc.split("\n")[0] if doc else "",
                        })
            
            # Extract version
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__version__":
                            if isinstance(node.value, ast.Constant):
                                info["version"] = str(node.value.value)

        except SyntaxError:
            pass
    
    # Find submodules (subdirectories with __init__.py)
    for child in sorted(module_dir.iterdir()):
        if child.is_dir() and (child / "__init__.py").exists():
            sub_doc = ""
            sub_init = child / "__init__.py"
            try:
                sub_tree = ast.parse(sub_init.read_text())
                if (sub_tree.body and isinstance(sub_tree.body[0], ast.Expr)
                        and isinstance(sub_tree.body[0].value, (ast.Constant, ast.Str))):
                    raw = sub_tree.body[0].value.value if isinstance(sub_tree.body[0].value, ast.Constant) else sub_tree.body[0].value.s
                    sub_doc = raw.strip().split("\n")[0]
            except (SyntaxError, Exception):
                pass
            info["submodules"].append({"name": child.name, "doc": sub_doc})

    # Find all .py files
    for py_file in sorted(module_dir.glob("*.py")):
        if py_file.name != "__init__.py":
            info["py_files"].append(py_file.name)
    
    return info


def get_module_description(info: dict) -> str:
    """Get a one-line description from the docstring."""
    ds = info["docstring"]
    if ds:
        # Get the first non-empty line after the title
        lines = ds.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("Submodule") and stripped != info["display_name"] and stripped != info["name"]:
                # Skip title-like lines
                if stripped.lower().replace("_", " ") == info["name"].replace("_", " "):
                    continue
                if stripped.endswith("Module") or stripped.endswith("module"):
                    continue
                return stripped
    return f"Provides {info['display_name'].lower()} functionality for the Codomyrmex ecosystem."


def generate_readme(info: dict) -> str:
    """Generate enriched README.md content."""
    desc = get_module_description(info)
    
    lines = [
        f"# {info['display_name']} Module Documentation",
        "",
        f"**Version**: v{info['version']} | **Status**: Active | **Last Updated**: February 2026",
        "",
        "## Overview",
        "",
        f"{desc}",
        "",
    ]
    
    # Key Features
    features = []
    for cls in info["classes"][:6]:
        if cls["doc"]:
            features.append(f"- **{cls['name']}** — {cls['doc']}")
        else:
            features.append(f"- **{cls['name']}** — {cls['name'].replace('_', ' ')}")
    for fn in info["functions"][:4]:
        if fn["doc"]:
            features.append(f"- `{fn['name']}()` — {fn['doc']}")
        else:
            features.append(f"- `{fn['name']}()` — {fn['name'].replace('_', ' ')}")
    
    if features:
        lines.append("## Key Features")
        lines.append("")
        lines.extend(features)
        lines.append("")
    
    # Submodules
    if info["submodules"]:
        lines.append("## Submodules")
        lines.append("")
        lines.append("| Submodule | Description |")
        lines.append("|-----------|-------------|")
        for sub in info["submodules"]:
            doc = sub["doc"] or sub["name"].replace("_", " ").title()
            lines.append(f"| `{sub['name']}` | {doc} |")
        lines.append("")
    
    # Quick Start
    lines.append("## Quick Start")
    lines.append("")
    lines.append("```python")
    if info["classes"]:
        imports = ", ".join(c["name"] for c in info["classes"][:3])
        lines.append(f"from codomyrmex.{info['name']} import {imports}")
        lines.append("")
        first_cls = info["classes"][0]["name"]
        lines.append(f"# Initialize")
        lines.append(f"instance = {first_cls}()")
    elif info["functions"]:
        imports = ", ".join(f["name"] for f in info["functions"][:3])
        lines.append(f"from codomyrmex.{info['name']} import {imports}")
        lines.append("")
        first_fn = info["functions"][0]["name"]
        lines.append(f"# Use the module")
        lines.append(f"result = {first_fn}()")
    else:
        lines.append(f"from codomyrmex.{info['name']} import *  # See source for specific imports")
    lines.append("```")
    lines.append("")
    
    # API Reference (if enough classes/functions)
    if len(info["classes"]) > 2 or len(info["functions"]) > 2:
        lines.append("## API Reference")
        lines.append("")
        if info["classes"]:
            lines.append("### Classes")
            lines.append("")
            lines.append("| Class | Description |")
            lines.append("|-------|-------------|")
            for cls in info["classes"]:
                doc = cls["doc"] or cls["name"].replace("_", " ")
                lines.append(f"| `{cls['name']}` | {doc} |")
            lines.append("")
        if info["functions"]:
            lines.append("### Functions")
            lines.append("")
            lines.append("| Function | Description |")
            lines.append("|----------|-------------|")
            for fn in info["functions"]:
                doc = fn["doc"] or fn["name"].replace("_", " ")
                lines.append(f"| `{fn['name']}()` | {doc} |")
            lines.append("")
    
    # Directory Contents
    lines.append("## Directory Contents")
    lines.append("")
    lines.append("| File | Description |")
    lines.append("|------|-------------|")
    lines.append("| `README.md` | This documentation |")
    lines.append("| `AGENTS.md` | Agent coordination guide |")
    lines.append("| `SPEC.md` | Technical specification |")
    
    # Check for extra files in docs dir
    docs_dir = DOCS_ROOT / info["name"]
    if docs_dir.exists():
        for child in sorted(docs_dir.iterdir()):
            if child.is_dir():
                lines.append(f"| `{child.name}/` | {child.name.replace('_', ' ').title()} |")
    lines.append("")
    
    # Navigation
    lines.append("## Navigation")
    lines.append("")
    lines.append(f"- **Source**: [src/codomyrmex/{info['name']}/](../../../src/codomyrmex/{info['name']}/)")
    lines.append("- **Parent**: [Modules](../README.md)")
    lines.append("")
    
    return "\n".join(lines)


def generate_agents(info: dict) -> str:
    """Generate enriched AGENTS.md content."""
    desc = get_module_description(info)
    
    lines = [
        f"# {info['display_name']} Module — Agent Coordination",
        "",
        "## Purpose",
        "",
        f"{desc}",
        "",
        "## Key Capabilities",
        "",
    ]
    
    # Capabilities from classes + functions
    caps = []
    for cls in info["classes"][:5]:
        doc = cls["doc"] or cls["name"].replace("_", " ")
        caps.append(f"- **{cls['name']}**: {doc}")
    for fn in info["functions"][:3]:
        doc = fn["doc"] or fn["name"].replace("_", " ")
        caps.append(f"- `{fn['name']}()`: {doc}")
    
    if caps:
        lines.extend(caps)
    else:
        lines.append(f"- {info['display_name']} operations and management")
    lines.append("")
    
    # Agent Usage
    lines.append("## Agent Usage Patterns")
    lines.append("")
    lines.append("```python")
    if info["classes"]:
        cls_name = info["classes"][0]["name"]
        lines.append(f"from codomyrmex.{info['name']} import {cls_name}")
        lines.append("")
        lines.append(f"# Agent initializes {info['display_name'].lower()}")
        lines.append(f"instance = {cls_name}()")
    else:
        lines.append(f"from codomyrmex.{info['name']} import *")
        lines.append("")
        lines.append(f"# Agent uses {info['display_name'].lower()} capabilities")
    lines.append("```")
    lines.append("")
    
    # Integration
    lines.append("## Integration Points")
    lines.append("")
    lines.append(f"- **Source**: [src/codomyrmex/{info['name']}/](../../../src/codomyrmex/{info['name']}/)")
    lines.append("- **Docs**: [Module Documentation](README.md)")
    lines.append("- **Spec**: [Technical Specification](SPEC.md)")
    lines.append("")
    
    return "\n".join(lines)


def generate_spec(info: dict) -> str:
    """Generate enriched SPEC.md content."""
    desc = get_module_description(info)
    
    lines = [
        f"# {info['display_name']} — Functional Specification",
        "",
        f"**Module**: `codomyrmex.{info['name']}`  ",
        f"**Version**: v{info['version']}  ",
        "**Status**: Active",
        "",
        "## 1. Overview",
        "",
        f"{desc}",
        "",
        "## 2. Architecture",
        "",
    ]
    
    # Architecture table
    if info["classes"] or info["py_files"]:
        lines.append("### Components")
        lines.append("")
        lines.append("| Component | Type | Description |")
        lines.append("|-----------|------|-------------|")
        for cls in info["classes"][:10]:
            doc = cls["doc"] or cls["name"].replace("_", " ")
            lines.append(f"| `{cls['name']}` | Class | {doc} |")
        for fn in info["functions"][:5]:
            doc = fn["doc"] or fn["name"].replace("_", " ")
            lines.append(f"| `{fn['name']}()` | Function | {doc} |")
        lines.append("")
    
    # Submodules
    if info["submodules"]:
        lines.append("### Submodule Structure")
        lines.append("")
        for sub in info["submodules"]:
            doc = sub["doc"] or sub["name"].replace("_", " ").title()
            lines.append(f"- `{sub['name']}/` — {doc}")
        lines.append("")
    
    # Source files
    if info["py_files"]:
        lines.append("### Source Files")
        lines.append("")
        for f in info["py_files"][:10]:
            lines.append(f"- `{f}`")
        if len(info["py_files"]) > 10:
            lines.append(f"- ...and {len(info['py_files']) - 10} more")
        lines.append("")
    
    # Dependencies
    lines.append("## 3. Dependencies")
    lines.append("")
    lines.append(f"See `src/codomyrmex/{info['name']}/__init__.py` for import dependencies.")
    lines.append("")
    
    # API
    lines.append("## 4. Public API")
    lines.append("")
    if info["classes"]:
        imports = ", ".join(c["name"] for c in info["classes"][:5])
        lines.append(f"```python")
        lines.append(f"from codomyrmex.{info['name']} import {imports}")
        lines.append(f"```")
    elif info["functions"]:
        imports = ", ".join(f["name"] for f in info["functions"][:5])
        lines.append(f"```python")
        lines.append(f"from codomyrmex.{info['name']} import {imports}")
        lines.append(f"```")
    else:
        lines.append(f"See source module for available exports.")
    lines.append("")
    
    # Testing
    lines.append("## 5. Testing")
    lines.append("")
    lines.append("```bash")
    lines.append(f"uv run python -m pytest src/codomyrmex/tests/ -k {info['name']} -v")
    lines.append("```")
    lines.append("")
    
    return "\n".join(lines)


def should_enrich(module_name: str, doc_file: Path, info: dict) -> bool:
    """Decide whether a doc file needs enrichment."""
    if not doc_file.exists():
        return True
    content = doc_file.read_text()
    lines_count = content.count("\n")
    
    # Always enrich if title is wrong
    first_line = content.split("\n")[0] if content else ""
    expected_display = info["display_name"]
    if first_line and expected_display.lower() not in first_line.lower() and module_name not in first_line.lower():
        return True
    
    # Enrich if very thin (under 50 lines for README, 25 for AGENTS/SPEC)
    if doc_file.name == "README.md" and lines_count < 50:
        return True
    if doc_file.name in ("AGENTS.md", "SPEC.md") and lines_count < 25:
        return True
    
    return False


def main():
    enriched_count = 0
    skipped_count = 0
    
    modules = sorted([d.name for d in SRC_ROOT.iterdir() 
                       if d.is_dir() and d.name != "__pycache__" and (d / "__init__.py").exists()])
    
    print(f"Found {len(modules)} source modules")
    
    for mod_name in modules:
        src_dir = SRC_ROOT / mod_name
        docs_dir = DOCS_ROOT / mod_name
        
        if not docs_dir.exists():
            print(f"  ⚠️ No docs dir for {mod_name}, skipping")
            continue
        
        info = extract_module_info(src_dir)
        
        # README.md
        readme_path = docs_dir / "README.md"
        if should_enrich(mod_name, readme_path, info):
            readme_content = generate_readme(info)
            readme_path.write_text(readme_content)
            enriched_count += 1
            print(f"  ✅ Enriched {mod_name}/README.md ({readme_content.count(chr(10))} lines)")
        else:
            skipped_count += 1
        
        # AGENTS.md
        agents_path = docs_dir / "AGENTS.md"
        if should_enrich(mod_name, agents_path, info):
            agents_content = generate_agents(info)
            agents_path.write_text(agents_content)
            enriched_count += 1
            print(f"  ✅ Enriched {mod_name}/AGENTS.md ({agents_content.count(chr(10))} lines)")
        else:
            skipped_count += 1
        
        # SPEC.md
        spec_path = docs_dir / "SPEC.md"
        if should_enrich(mod_name, spec_path, info):
            spec_content = generate_spec(info)
            spec_path.write_text(spec_content)
            enriched_count += 1
            print(f"  ✅ Enriched {mod_name}/SPEC.md ({spec_content.count(chr(10))} lines)")
        else:
            skipped_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Enriched: {enriched_count} files")
    print(f"⏭️ Skipped (already rich): {skipped_count} files")
    print(f"📊 Total processed: {enriched_count + skipped_count} files")


if __name__ == "__main__":
    main()
