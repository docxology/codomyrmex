"""
Static analysis for imports and dependency graph.
"""

import ast
import os
from pathlib import Path
from typing import Any
import logging

logger = logging.getLogger(__name__)

# Layer sets aligned with src/codomyrmex/SPEC.md architecture
# exceptions and validation are cross-cutting foundation concerns used by all layers
FOUNDATION = {
    "config_management", "environment_setup", "exceptions", "logging_monitoring",
    "model_context_protocol", "telemetry", "terminal_interface", "validation",
}
CORE = {
    "cache", "coding", "compression", "data_visualization", "documents",
    "encryption", "git_operations", "llm", "networking", "performance",
    "scrape", "search", "security", "serialization", "static_analysis",
}
SERVICE = {
    "api", "auth", "ci_cd_automation", "cloud", "containerization",
    "database_management", "deployment", "documentation", "logistics",
    "orchestrator",
}
SPECIALIZED = {
    "agentic_memory", "agents", "audio", "bio_simulation", "cerebrum",
    "cli", "collaboration", "concurrency", "crypto", "dark", "defense",
    "dependency_injection", "edge_computing", "embodiment", "events",
    "evolutionary_ai", "examples", "feature_flags",
    "finance", "formal_verification", "fpf", "graph_rag", "ide",
    "identity", "maintenance", "market", "meme", "model_ops",
    "module_template", "networks", "physical_management", "plugin_system",
    "privacy", "prompt_engineering", "quantum", "relations", "simulation",
    "skills", "spatial", "system_discovery", "templating", "testing",
    "tests", "tool_use", "utils", "vector_store", "video",
    "wallet", "website",
}


def get_layer(module: str) -> str:
    """Determine the architectural layer of a module.

    Layers follow the hierarchy defined in SPEC.md:
    Foundation → Core → Service → Specialized
    """
    if module in FOUNDATION:
        return "foundation"
    elif module in CORE:
        return "core"
    elif module in SERVICE:
        return "service"
    elif module in SPECIALIZED:
        return "specialized"
    return "other"


def extract_imports_ast(filepath: Path) -> list[str]:
    """Extract imported codomyrmex module names using AST."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, str(filepath))
    except (SyntaxError, UnicodeDecodeError) as e:
        logger.debug("Skipping unreadable file %s: %s", filepath, e)
        return []

    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("codomyrmex."):
                parts = node.module.split(".")
                if len(parts) >= 2:
                    modules.append(parts[1])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("codomyrmex."):
                    parts = alias.name.split(".")
                    if len(parts) >= 2:
                        modules.append(parts[1])
    return modules


def scan_imports(src_dir: Path) -> list[dict[str, Any]]:
    """Scan all .py files and extract cross-module imports via AST."""
    edges = []
    for root, _dirs, files in os.walk(src_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = Path(root) / fname
            # Use safe relative_to
            try:
                rel = fpath.relative_to(src_dir)
            except ValueError:
                continue

            parts = rel.parts
            if len(parts) < 2:
                continue
            src_module = parts[0]
            if src_module == "__pycache__":
                continue

            for dst_module in extract_imports_ast(fpath):
                if dst_module == src_module:
                    continue
                edges.append({
                    "src": src_module,
                    "dst": dst_module,
                    "file": str(rel),
                    "src_layer": get_layer(src_module),
                    "dst_layer": get_layer(dst_module),
                })
    return edges


def check_layer_violations(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply layer-boundary rules and return violations.

    Rules (from SPEC.md):
    - Foundation modules must not import Core, Service, or Specialized modules
    - Core modules must not import Service or Specialized modules
    - Service modules must not import Specialized modules
    """
    # Higher number = higher layer (can't import upward)
    layer_rank = {"foundation": 0, "core": 1, "service": 2, "specialized": 3}
    violations = []
    for edge in edges:
        src_l = edge["src_layer"]
        dst_l = edge["dst_layer"]
        src_rank = layer_rank.get(src_l)
        dst_rank = layer_rank.get(dst_l)

        if src_rank is not None and dst_rank is not None and src_rank < dst_rank:
            reason = (
                f"{src_l.capitalize()} module '{edge['src']}' "
                f"imports {dst_l} module '{edge['dst']}'"
            )
            violations.append({**edge, "reason": reason})

    return violations
