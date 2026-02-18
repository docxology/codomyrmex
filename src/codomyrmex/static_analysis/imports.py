"""
Static analysis for imports and dependency graph.
"""

import ast
import os
import json
from pathlib import Path
from typing import List, Dict, Any

INFRA = {"logging_monitoring", "validation", "events", "config_management", "exceptions", "utils"}
CORE = {"agents", "coding", "security"}
SPECIALIZED = {
    "cerebrum", "meme", "bio_simulation", "finance", "quantum",
    "spatial", "embodiment", "evolutionary_ai", "market",
}
APPLICATION = {"cli", "api", "website", "orchestrator"}


def get_layer(module: str) -> str:
    """Determine the architectural layer of a module."""
    if module in INFRA:
        return "infra"
    elif module in CORE:
        return "core"
    elif module in SPECIALIZED:
        return "specialized"
    elif module in APPLICATION:
        return "application"
    return "other"


def extract_imports_ast(filepath: Path) -> List[str]:
    """Extract imported codomyrmex module names using AST."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, str(filepath))
    except (SyntaxError, UnicodeDecodeError):
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


def scan_imports(src_dir: Path) -> List[Dict[str, Any]]:
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


def check_layer_violations(edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply layer rules and return violations."""
    violations = []
    for edge in edges:
        src_l = edge["src_layer"]
        dst_l = edge["dst_layer"]
        reason = None

        if src_l == "infra" and dst_l in ("core", "specialized"):
            reason = f"Infrastructure '{edge['src']}' imports {dst_l} '{edge['dst']}'"
        elif src_l == "core" and dst_l == "specialized":
            reason = f"Core '{edge['src']}' imports specialized '{edge['dst']}'"

        if reason:
            violations.append({**edge, "reason": reason})

    return violations
