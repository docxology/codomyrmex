#!/usr/bin/env python3
"""
scripts/restore_descriptions.py

Restores the descriptive text for modules in README.md that was overwritten.
"""

import argparse
from pathlib import Path
from codomyrmex.utils.cli_helpers import print_success, print_error

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

def main():
    parser = argparse.ArgumentParser(description="Restore module descriptions in README.md.")
    parser.add_argument("--root", type=Path, default=Path(__file__).parent.parent, help="Project root directory")
    args = parser.parse_args()

    root_dir = args.root
    readme_path = root_dir / "src" / "codomyrmex" / "README.md"
    
    if not readme_path.exists():
        print_error(f"README.md not found at {readme_path}")
        return

    content = readme_path.read_text()
    
    for module, desc in DESCRIPTIONS.items():
        # Replace generic "Module" with specific description
        # Search for "- `module/` – Module"
        target = f"- `{module}/` – Module"
        replacement = f"- `{module}/` – {desc}"
        content = content.replace(target, replacement)
        
    readme_path.write_text(content)
    print_success("Restored descriptions in README.md")

if __name__ == "__main__":
    main()
