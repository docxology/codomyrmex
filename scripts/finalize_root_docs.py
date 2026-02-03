#!/usr/bin/env python3
"""
scripts/finalize_root_docs.py

Finalizes root documentation by:
1. Updating AGENTS.md with rich descriptions.
2. Updating SPEC.md with the complete module list.
"""

from pathlib import Path
import re

ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src" / "codomyrmex"
AGENTS_PATH = SRC_DIR / "AGENTS.md"
SPEC_PATH = SRC_DIR / "SPEC.md"

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

def update_agents_md():
    content = AGENTS_PATH.read_text()
    
    for module, desc in DESCRIPTIONS.items():
        # Replace generic "Module component" with specific description
        target = f"- `{module}/` – Module component"
        replacement = f"- `{module}/` – {desc}"
        content = content.replace(target, replacement)
        
    AGENTS_PATH.write_text(content)
    print("Updated AGENTS.md descriptions.")

def update_spec_md():
    # SPEC.md has a "Specialized Layer - Advanced Features" section in mermaid and text
    # It's hard to automatically parse/update the text descriptions without potential damage.
    # But we can look for the huge list of modules and see if we can perform targeted updates.
    # The SPEC already contains a good list.
    # Let's check for missing *new* modules in the list manually first?
    # Or just print what is missing.
    
    content = SPEC_PATH.read_text()
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
    update_agents_md()
    update_spec_md()

if __name__ == "__main__":
    main()
