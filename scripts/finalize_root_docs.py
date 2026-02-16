#!/usr/bin/env python3
"""
scripts/finalize_root_docs.py

Finalizes root documentation by:
1. Updating AGENTS.md with rich descriptions.
2. Updating SPEC.md with the complete module list.
"""

import argparse
from pathlib import Path
import re

DESCRIPTIONS = {
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

def update_agents_md(src_dir: Path):
    agents_path = src_dir / "AGENTS.md"
    if not agents_path.exists():
        print(f"Skipping AGENTS.md update: {agents_path} not found")
        return

    content = agents_path.read_text()
    
    for module, desc in DESCRIPTIONS.items():
        # Replace generic "Module component" with specific description
        target = f"- `{module}/` – Module component"
        replacement = f"- `{module}/` – {desc}"
        content = content.replace(target, replacement)
        
    agents_path.write_text(content)
    print("Updated AGENTS.md descriptions.")

def update_spec_md(src_dir: Path):
    spec_path = src_dir / "SPEC.md"
    if not spec_path.exists():
        print(f"Skipping SPEC.md update: {spec_path} not found")
        return

    content = spec_path.read_text()
    missing = []
    for module in DESCRIPTIONS.keys():
        if f"`{module}`" not in content and f"{module}<br/>" not in content:
            missing.append(module)
            
    if missing:
        print(f"WARNING: The following modules are missing from SPEC.md: {missing}")
        # We will not auto-update SPEC.md structure as it's complex, but we flag it.
    else:
        print("SPEC.md appears to cover all modules (based on name check).")

def main():
    parser = argparse.ArgumentParser(description="Finalize root documentation.")
    parser.add_argument("--root", type=Path, default=Path(__file__).parent.parent, help="Project root directory")
    args = parser.parse_args()

    root_dir = args.root
    src_dir = root_dir / "src" / "codomyrmex"
    
    if not src_dir.exists():
        print(f"Error: Source directory {src_dir} does not exist.")
        return

    update_agents_md(src_dir)
    update_spec_md(src_dir)

if __name__ == "__main__":
    main()
