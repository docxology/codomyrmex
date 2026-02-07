#!/usr/bin/env python3
"""Add cross-references to SPEC.md files and Related Modules to README/AGENTS."""
import os
import re
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

def find_related(mod):
    """Find modules imported by this module's __init__.py."""
    init = os.path.join(SRC, mod, "__init__.py")
    if not os.path.exists(init):
        return []
    try:
        with open(init) as f:
            content = f.read()
        return sorted(set(re.findall(r"from codomyrmex\.(\w+)", content)) - {mod})
    except Exception:
        return []

def main():
    modules = sorted(
        d for d in os.listdir(DOCS)
        if os.path.isdir(os.path.join(DOCS, d))
    )
    
    spec_fixed = 0
    readme_fixed = 0
    agents_fixed = 0
    
    for mod in modules:
        mod_docs = os.path.join(DOCS, mod)
        related = find_related(mod)
        
        # 1. Add References to SPEC.md
        spec_path = os.path.join(mod_docs, "SPEC.md")
        if os.path.exists(spec_path):
            with open(spec_path) as f:
                content = f.read()
            if "README.md" not in content:
                ref = f"\n## References\n\n"
                ref += f"- [README.md](README.md) — Human-readable documentation\n"
                ref += f"- [AGENTS.md](AGENTS.md) — Agent coordination guide\n"
                ref += f"- [Source Code](../../../src/codomyrmex/{mod}/)\n"
                with open(spec_path, "w") as f:
                    f.write(content.rstrip() + "\n" + ref)
                spec_fixed += 1
        
        # 2. Add Related Modules to README.md
        readme_path = os.path.join(mod_docs, "README.md")
        if os.path.exists(readme_path) and related:
            with open(readme_path) as f:
                content = f.read()
            if "Related Modules" not in content and "## Navigation" in content:
                section = "\n## Related Modules\n\n"
                for r in related[:6]:
                    disp = DISPLAY.get(r, r.replace("_", " ").title())
                    section += f"- [{disp}](../{r}/README.md)\n"
                content = content.replace("## Navigation", section + "\n## Navigation")
                with open(readme_path, "w") as f:
                    f.write(content)
                readme_fixed += 1
        
        # 3. Add Related Modules to AGENTS.md
        agents_path = os.path.join(mod_docs, "AGENTS.md")
        if os.path.exists(agents_path) and related:
            with open(agents_path) as f:
                content = f.read()
            if "Related Modules" not in content and "related" not in content.lower():
                section = "\n## Related Modules\n\n"
                for r in related[:6]:
                    disp = DISPLAY.get(r, r.replace("_", " ").title())
                    section += f"- [{disp}](../{r}/AGENTS.md)\n"
                with open(agents_path, "w") as f:
                    f.write(content.rstrip() + "\n" + section)
                agents_fixed += 1
        
        sys.stdout.write(".")
        sys.stdout.flush()
    
    print()
    print(f"✅ SPEC.md: Added References to {spec_fixed} files")
    print(f"✅ README.md: Added Related Modules to {readme_fixed} files")
    print(f"✅ AGENTS.md: Added Related Modules to {agents_fixed} files")
    print(f"📊 Total improvements: {spec_fixed + readme_fixed + agents_fixed}")

if __name__ == "__main__":
    main()
