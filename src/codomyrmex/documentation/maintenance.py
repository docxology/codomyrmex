"""
Maintenance utilities for documentation synchronization.
"""

from pathlib import Path

# Shared descriptions mapping
MODULE_DESCRIPTIONS = {
    "agentic_memory": "Memory systems for AI agents",
    "agents": "Agentic framework integrations",
    "api": "API infrastructure and resilience",
    "auth": "Authentication and authorization",
    "build_synthesis": "Build automation",
    "cache": "Caching infrastructure",
    "cerebrum": "Case-based reasoning",
    "ci_cd_automation": "CI/CD pipelines",
    "cli": "Command line interface",
    "cloud": "Cloud provider integration",
    "coding": "Code execution and review",
    "collaboration": "Team collaboration",
    "compression": "Data compression",
    "concurrency": "Concurrency utilities",
    "config_management": "Configuration management",
    "containerization": "Container management",
    "cost_management": "Cost tracking and budgets",
    "data_lineage": "Data lineage tracking",
    "data_visualization": "Charts and plots",
    "database_management": "Database operations",
    "deployment": "Deployment automation",
    "documentation": "Documentation generation",
    "documents": "Document processing",
    "embodiment": "Physical embodiment",
    "encryption": "Data encryption",
    "environment_setup": "Environment validation",
    "events": "Event system",
    "evolutionary_ai": "Evolutionary algorithms",
    "examples": "Usage examples",
    "feature_flags": "Feature flag management",
    "feature_store": "ML feature storage",
    "fpf": "Functional programming framework",
    "git_operations": "Git automation",
    "graph_rag": "Graph-based RAG",
    "ide": "IDE integration",
    "inference_optimization": "Inference caching/batching",
    "llm": "LLM infrastructure",
    "logging_monitoring": "Centralized logging",
    "logistics": "Workflow logistics",
    "metrics": "Metrics collection",
    "migration": "Data migration",
    "model_context_protocol": "MCP interfaces",
    "model_ops": "ML model operations",
    "model_registry": "Model versioning",
    "module_template": "Module scaffolding",
    "multimodal": "Multimodal processing",
    "networking": "Network utilities",
    "notification": "Notification channels",
    "observability_dashboard": "Dashboards and alerts",
    "orchestrator": "Workflow orchestration",
    "pattern_matching": "Code pattern analysis",
    "performance": "Performance monitoring",
    "physical_management": "Physical systems",
    "plugin_system": "Plugin architecture",
    "prompt_testing": "Prompt evaluation",
    "scrape": "Web scraping",
    "security": "Security scanning",
    "serialization": "Data serialization",
    "skills": "Agent skills",
    "spatial": "3D/4D modeling",
    "static_analysis": "Code quality",
    "system_discovery": "Module discovery",
    "telemetry": "Telemetry and tracing",
    "templating": "Template management",
    "terminal_interface": "Terminal UI",
    "testing": "Test utilities",
    "tests": "Test suites",
    "tools": "Utility tools",
    "tree_sitter": "Tree-sitter parsing",
    "utils": "General utilities",
    "validation": "Input validation",
    "website": "Website generation",
    "workflow_testing": "Workflow testing",
}

IGNORE_DIRS = ["__pycache__", ".DS_Store"]


def get_submodules(src_dir: Path) -> list[str]:
    """Get list of valid submodule names."""
    modules = []
    for item in src_dir.iterdir():
        if item.is_dir() and item.name not in IGNORE_DIRS and not item.name.startswith("."):
            if (item / "__init__.py").exists():
                modules.append(item.name)
    return sorted(modules)


def update_init_py(modules: list[str], src_dir: Path):
    """Update __init__.py with module list."""
    init_path = src_dir / "__init__.py"
    if not init_path.exists():
        print(f"Skipping __init__.py update: {init_path} not found")
        return

    content = init_path.read_text(encoding="utf-8")

    # Generate new lists
    submodules_list = "    " + ',\n    '.join([f'"{m}"' for m in modules]) + ",\n"
    all_list = "    " + ',\n    '.join([f'"{m}"' for m in modules]) + ",\n"

    start_marker = "_submodules = ["
    end_marker = "]"

    try:
        start_idx = content.find(start_marker) + len(start_marker)
        end_idx = content.find(end_marker, start_idx)

        if start_idx == -1 or end_idx == -1:
            print("Could not find _submodules list in __init__.py")
            return

        new_content = content[:start_idx] + "\n" + submodules_list + content[end_idx:]

        # Now find __all__
        start_marker_all = "__all__ = ["
        start_idx_all = new_content.find(start_marker_all) + len(start_marker_all)
        end_idx_all = new_content.find(end_marker, start_idx_all)

        if start_idx_all == -1 or end_idx_all == -1:
             print("Could not find __all__ list in __init__.py")
             return

        # Preserve static exports (heuristic)
        static_exports = [
            '    "get_version",',
            '    "get_module_path",',
            '    "list_modules",'
        ]

        final_all_content = all_list + '\n'.join(static_exports) + "\n"
        final_content = new_content[:start_idx_all] + "\n" + final_all_content + new_content[end_idx_all:]

        init_path.write_text(final_content, encoding="utf-8")
        print("Updated __init__.py")

    except Exception as e:
        print(f"Error updating __init__.py: {e}")


def update_readme_md(modules: list[str], src_dir: Path):
    """Update README.md directory contents."""
    readme_path = src_dir / "README.md"
    if not readme_path.exists():
        print(f"Skipping README.md update: {readme_path} not found")
        return

    content = readme_path.read_text(encoding="utf-8")

    header = "## Directory Contents\n\n"
    start_idx = content.find(header)
    if start_idx == -1:
        print("Could not find Directory Contents in README.md")
        return

    start_idx += len(header)
    end_idx = content.find("## ", start_idx)
    if end_idx == -1:
        end_idx = len(content)

    new_list = ""
    new_list += "- `PAI.md` – Personal AI Infrastructure documentation\n"
    new_list += "- `README.md` – This file\n"
    new_list += "- `SPEC.md` – Module specification\n"
    new_list += "- `__init__.py` – Package initialization\n"

    for m in modules:
        new_list += f"- `{m}/` – Module\n"

    final_content = content[:start_idx] + new_list + "\n" + content[end_idx:]
    readme_path.write_text(final_content, encoding="utf-8")
    print("Updated README.md")


def update_agents_md_list(modules: list[str], src_dir: Path):
    """Update AGENTS.md component list."""
    agents_path = src_dir / "AGENTS.md"
    if not agents_path.exists():
         print(f"Skipping AGENTS.md update: {agents_path} not found")
         return

    content = agents_path.read_text(encoding="utf-8")

    header = "## Active Components\n\n"
    start_idx = content.find(header)
    if start_idx == -1:
        print("Could not find Active Components in AGENTS.md")
        return

    start_idx += len(header)
    end_idx = content.find("## ", start_idx)
    if end_idx == -1:
        end_idx = len(content)

    new_list = ""
    new_list += "- `PAI.md` – Project file\n"
    new_list += "- `README.md` – Project file\n"
    new_list += "- `SPEC.md` – Project file\n"
    new_list += "- `__init__.py` – Project file\n"

    for m in modules:
        new_list += f"- `{m}/` – Module component\n"

    final_content = content[:start_idx] + new_list + "\n" + content[end_idx:]
    agents_path.write_text(final_content, encoding="utf-8")
    print("Updated AGENTS.md list")


def enrich_agents_md(src_dir: Path):
    """Update AGENTS.md with rich descriptions."""
    agents_path = src_dir / "AGENTS.md"
    if not agents_path.exists():
        print(f"Skipping AGENTS.md update: {agents_path} not found")
        return

    content = agents_path.read_text(encoding="utf-8")

    for module, desc in MODULE_DESCRIPTIONS.items():
        # Replace generic "Module component" with specific description
        target = f"- `{module}/` – Module component"
        replacement = f"- `{module}/` – {desc}"
        content = content.replace(target, replacement)

    agents_path.write_text(content, encoding="utf-8")
    print("Updated AGENTS.md descriptions.")


def update_root_docs(src_dir: Path):
    """Main entry point for basic root doc updates."""
    modules = get_submodules(src_dir)
    print(f"Found {len(modules)} submodules.")
    update_init_py(modules, src_dir)
    update_readme_md(modules, src_dir)
    update_agents_md_list(modules, src_dir)


def finalize_docs(src_dir: Path):
    """Main entry point for finalizing docs (rich descriptions + spec check)."""
    enrich_agents_md(src_dir)
    update_spec(src_dir)


def update_spec(src_dir: Path):
    """Update SPEC.md with missing modules."""
    spec_path = src_dir / "SPEC.md"
    if not spec_path.exists():
        print(f"Error: SPEC.md not found at {spec_path}")
        return

    content = spec_path.read_text(encoding="utf-8")
    modules = get_submodules(src_dir)

    start_marker = "#### Specialized Layer"
    modules_marker = "**Modules**:"

    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Could not find Specialized Layer section")
        return

    modules_idx = content.find(modules_marker, start_idx)
    if modules_idx == -1:
        print("Could not find Modules list in Specialized Layer section")
        return

    modules_idx += len(modules_marker)

    end_idx = content.find("**Characteristics**", modules_idx)
    if end_idx == -1:
        end_idx = len(content)

    current_list_block = content[modules_idx:end_idx]

    existing_modules = set()
    for m in modules:
        if f"`{m}`" in content or f"`{m}<" in content or f"[{m}]" in content:
            existing_modules.add(m)

    missing = set(modules) - existing_modules

    if missing:
        print(f"Adding {len(missing)} missing modules to Specialized Layer: {missing}")
        new_entries = ""
        for m in sorted(missing):
            new_entries += f"\n- `{m}`: Specialized module"

        new_list_block = current_list_block.rstrip() + new_entries + "\n\n"
        final_content = content[:modules_idx] + new_list_block + content[end_idx:]
        spec_path.write_text(final_content, encoding="utf-8")
        print("Updated SPEC.md")
    else:
        print("No missing modules found in SPEC.md")
