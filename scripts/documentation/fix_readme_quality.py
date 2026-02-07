#!/usr/bin/env python3
"""Fix duplicate entries in API tables and enrich thin README files."""
import ast
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = os.path.join(REPO, "docs", "modules")
SRC = os.path.join(REPO, "src", "codomyrmex")

DISPLAY = {
    "accessibility": "Accessibility", "agentic_memory": "Agentic Memory",
    "agents": "AI Agents", "api": "API", "audio": "Audio Processing",
    "auth": "Authentication", "build_synthesis": "Build Synthesis",
    "cache": "Cache", "cerebrum": "Cerebrum", "chaos_engineering": "Chaos Engineering",
    "ci_cd_automation": "CI/CD Automation", "cli": "CLI", "cloud": "Cloud",
    "coding": "Coding", "collaboration": "Collaboration", "compression": "Compression",
    "concurrency": "Concurrency", "config_management": "Config Management",
    "containerization": "Containerization", "cost_management": "Cost Management",
    "dark": "Dark", "data_lineage": "Data Lineage",
    "data_visualization": "Data Visualization", "database_management": "Database Management",
    "defense": "Defense", "deployment": "Deployment", "documentation": "Documentation",
    "documents": "Documents", "edge_computing": "Edge Computing",
    "embodiment": "Embodiment", "encryption": "Encryption",
    "environment_setup": "Environment Setup", "events": "Events",
    "evolutionary_ai": "Evolutionary AI", "examples": "Examples",
    "feature_flags": "Feature Flags", "feature_store": "Feature Store",
    "fpf": "FPF", "git_operations": "Git Operations", "graph_rag": "Graph RAG",
    "i18n": "i18n", "ide": "IDE Integration", "identity": "Identity",
    "inference_optimization": "Inference Optimization", "llm": "LLM",
    "logging_monitoring": "Logging & Monitoring", "logistics": "Logistics",
    "market": "Market", "metrics": "Metrics", "migration": "Migration",
    "model_context_protocol": "Model Context Protocol", "model_ops": "Model Ops",
    "model_registry": "Model Registry", "module_template": "Module Template",
    "multimodal": "Multimodal", "networking": "Networking",
    "notification": "Notification", "observability_dashboard": "Observability Dashboard",
    "orchestrator": "Orchestrator", "pattern_matching": "Pattern Matching",
    "performance": "Performance", "physical_management": "Physical Management",
    "plugin_system": "Plugin System", "privacy": "Privacy",
    "prompt_testing": "Prompt Testing", "quantum": "Quantum",
    "rate_limiting": "Rate Limiting", "scheduler": "Scheduler", "scrape": "Scrape",
    "search": "Search", "security": "Security", "serialization": "Serialization",
    "service_mesh": "Service Mesh", "skills": "Skills",
    "smart_contracts": "Smart Contracts", "spatial": "Spatial",
    "static_analysis": "Static Analysis", "streaming": "Streaming",
    "system_discovery": "System Discovery", "telemetry": "Telemetry",
    "templating": "Templating", "terminal_interface": "Terminal Interface",
    "testing": "Testing", "tests": "Tests", "tools": "Tools",
    "tree_sitter": "Tree-sitter", "utils": "Utilities", "validation": "Validation",
    "vector_store": "Vector Store", "video": "Video", "wallet": "Wallet",
    "website": "Website", "workflow_testing": "Workflow Testing",
}


def get_module_info(mod_name):
    """Get module info from __init__.py using AST - top-level only."""
    init = os.path.join(SRC, mod_name, "__init__.py")
    if not os.path.exists(init):
        return {"desc": "", "classes": [], "functions": [], "submodules": [], "version": "0.1.0"}
    
    try:
        with open(init) as f:
            content = f.read()
        tree = ast.parse(content)
    except Exception:
        return {"desc": "", "classes": [], "functions": [], "submodules": [], "version": "0.1.0"}
    
    info = {"desc": "", "classes": [], "functions": [], "submodules": [], "version": "0.1.0"}
    
    # Module docstring
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
        raw = tree.body[0].value.value.strip()
        for line in raw.split("\n"):
            s = line.strip()
            if s and not s.endswith("Module") and s.lower().replace("_", " ") != mod_name.replace("_", " "):
                info["desc"] = s
                break
    
    if not info["desc"]:
        info["desc"] = f"{DISPLAY.get(mod_name, mod_name)} module."
    
    # Top-level classes and functions ONLY (not methods)
    seen_classes = set()
    seen_funcs = set()
    for node in tree.body:  # Only top-level, NOT ast.walk
        if isinstance(node, ast.ClassDef) and node.name not in seen_classes:
            doc = ast.get_docstring(node) or ""
            info["classes"].append((node.name, doc.split("\n")[0] if doc else ""))
            seen_classes.add(node.name)
        elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_") and node.name not in seen_funcs:
            doc = ast.get_docstring(node) or ""
            info["functions"].append((node.name, doc.split("\n")[0] if doc else ""))
            seen_funcs.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__version__" and isinstance(node.value, ast.Constant):
                    info["version"] = str(node.value.value)
    
    # Submodules
    mod_dir = os.path.join(SRC, mod_name)
    for child in sorted(os.listdir(mod_dir)):
        child_path = os.path.join(mod_dir, child)
        if os.path.isdir(child_path) and os.path.exists(os.path.join(child_path, "__init__.py")):
            sub_doc = ""
            try:
                sub_tree = ast.parse(open(os.path.join(child_path, "__init__.py")).read())
                if sub_tree.body and isinstance(sub_tree.body[0], ast.Expr) and isinstance(sub_tree.body[0].value, ast.Constant):
                    sub_doc = sub_tree.body[0].value.value.strip().split("\n")[0]
            except Exception:
                pass
            info["submodules"].append((child, sub_doc or child.replace("_", " ").title()))
    
    return info


def generate_enriched_readme(mod, info, display):
    """Generate a richer README.md with deduped API tables."""
    lines = [
        f"# {display} Module Documentation",
        "",
        f"**Version**: v{info['version']} | **Status**: Active | **Last Updated**: February 2026",
        "",
        "## Overview",
        "",
        info["desc"],
        "",
    ]
    
    # Key Features
    features = []
    for name, doc in info["classes"][:6]:
        features.append(f"- **{name}** — {doc or name}")
    for name, doc in info["functions"][:4]:
        features.append(f"- `{name}()` — {doc or name}")
    
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
        for name, doc in info["submodules"]:
            lines.append(f"| `{name}` | {doc} |")
        lines.append("")
    
    # Quick Start
    lines.append("## Quick Start")
    lines.append("")
    lines.append("```python")
    if info["classes"]:
        imports = ", ".join(c[0] for c in info["classes"][:3])
        lines.append(f"from codomyrmex.{mod} import {imports}")
        lines.append("")
        lines.append(f"# Initialize")
        lines.append(f"instance = {info['classes'][0][0]}()")
    elif info["functions"]:
        imports = ", ".join(f[0] for f in info["functions"][:3])
        lines.append(f"from codomyrmex.{mod} import {imports}")
        lines.append("")
        lines.append(f"result = {info['functions'][0][0]}()")
    else:
        lines.append(f"from codomyrmex.{mod} import *")
    lines.append("```")
    lines.append("")
    
    # API Reference (deduplicated)
    if len(info["classes"]) > 2 or len(info["functions"]) > 2:
        lines.append("## API Reference")
        lines.append("")
        if info["classes"]:
            lines.append("### Classes")
            lines.append("")
            lines.append("| Class | Description |")
            lines.append("|-------|-------------|")
            for name, doc in info["classes"]:
                lines.append(f"| `{name}` | {doc or name} |")
            lines.append("")
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
    
    return "\n".join(lines)


def fix_duplicates_in_readme(readme_path):
    """Remove duplicate function entries from API tables in an existing README."""
    with open(readme_path) as f:
        lines = f.readlines()
    
    new_lines = []
    seen_entries = set()
    in_func_table = False
    
    for line in lines:
        stripped = line.strip()
        
        # Detect function table header
        if "| Function |" in stripped:
            in_func_table = True
            seen_entries = set()
            new_lines.append(line)
            continue
        
        if in_func_table:
            if stripped.startswith("|---"):
                new_lines.append(line)
                continue
            if not stripped.startswith("|"):
                in_func_table = False
                new_lines.append(line)
                continue
            # Extract function name
            parts = stripped.split("|")
            if len(parts) > 1:
                fn_name = parts[1].strip()
                if fn_name in seen_entries:
                    continue  # Skip duplicate
                seen_entries.add(fn_name)
        
        new_lines.append(line)
    
    with open(readme_path, "w") as f:
        f.writelines(new_lines)


def main():
    modules = sorted(
        d for d in os.listdir(DOCS)
        if os.path.isdir(os.path.join(DOCS, d))
    )
    
    dupes_fixed = 0
    thin_fixed = 0
    
    for mod in modules:
        readme_path = os.path.join(DOCS, mod, "README.md")
        if not os.path.exists(readme_path):
            continue
        
        with open(readme_path) as f:
            content = f.read()
        line_count = content.count("\n")
        
        display = DISPLAY.get(mod, mod.replace("_", " ").title())
        
        # Fix duplicates
        if "| Function |" in content:
            # Check for actual duplicates
            func_lines = []
            in_table = False
            for line in content.split("\n"):
                if "| Function |" in line:
                    in_table = True
                    continue
                if in_table:
                    if not line.strip().startswith("|"):
                        in_table = False
                        continue
                    if line.strip().startswith("|---"):
                        continue
                    parts = line.split("|")
                    if len(parts) > 1:
                        func_lines.append(parts[1].strip())
            
            if len(func_lines) != len(set(func_lines)):
                fix_duplicates_in_readme(readme_path)
                dupes_fixed += 1
        
        # Enrich thin READMEs (under 30 lines)
        if line_count < 30:
            info = get_module_info(mod)
            new_content = generate_enriched_readme(mod, info, display)
            # Only write if we generated more content
            if new_content.count("\n") > line_count:
                with open(readme_path, "w") as f:
                    f.write(new_content)
                thin_fixed += 1
        
        sys.stdout.write(".")
        sys.stdout.flush()
    
    print()
    print(f"✅ Fixed duplicate API entries in {dupes_fixed} README files")
    print(f"✅ Enriched {thin_fixed} thin README files")
    print(f"📊 Total: {dupes_fixed + thin_fixed} improvements")


if __name__ == "__main__":
    main()
