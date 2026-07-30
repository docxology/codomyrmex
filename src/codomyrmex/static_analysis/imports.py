"""
Static analysis for imports and dependency graph.
"""

import ast
import os
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Layer sets aligned with src/codomyrmex/SPEC.md architecture.
FOUNDATION = {
    "config_management",
    "environment_setup",
    "exceptions",
    "logging_monitoring",
    "model_context_protocol",
    "telemetry",
    "terminal_interface",
    "validation",
}
CORE = {
    "cache",
    "coding",
    "compression",
    "data_visualization",
    "documents",
    "encryption",
    "git_operations",
    "llm",
    "networking",
    "performance",
    "scrape",
    "search",
    "security",
    "serialization",
    "static_analysis",
}
SERVICE = {
    "api",
    "auth",
    "ci_cd_automation",
    "cloud",
    "containerization",
    "database_management",
    "deployment",
    "documentation",
    "logistics",
    "orchestrator",
}
SPECIALIZED = {
    "agentic_memory",
    "agents",
    "audio",
    "bio_simulation",
    "cerebrum",
    "cli",
    "collaboration",
    "concurrency",
    "crypto",
    "dark",
    "defense",
    "dependency_injection",
    "edge_computing",
    "embodiment",
    "events",
    "evolutionary_ai",
    "examples",
    "feature_flags",
    "finance",
    "formal_verification",
    "fpf",
    "graph_rag",
    "ide",
    "identity",
    "maintenance",
    "market",
    "meme",
    "model_ops",
    "module_template",
    "networks",
    "physical_management",
    "plugin_system",
    "privacy",
    "prompt_engineering",
    "quantum",
    "relations",
    "simulation",
    "skills",
    "spatial",
    "system_discovery",
    "templating",
    "testing",
    "tests",
    "tool_use",
    "utils",
    "vector_store",
    "video",
    "wallet",
    "website",
}

InterfaceContractKey = tuple[str, str, str]

# Exceptional upward imports are allowed only at these exact integration
# surfaces. Values explain the interface boundary; audit_imports.py also
# rejects entries that become stale after a refactor.
UPWARD_INTERFACE_CONTRACTS: Mapping[InterfaceContractKey, str] = MappingProxyType(
    {
        (
            "cloud",
            "identity",
            "cloud/infomaniak/security.py",
        ): "Optional Infomaniak identity-verification adapter.",
        (
            "cloud",
            "privacy",
            "cloud/infomaniak/security.py",
        ): "Optional Infomaniak privacy-cleaning adapter.",
        (
            "coding",
            "agents",
            "coding/debugging/patch_generator.py",
        ): "Typed agent-request boundary for patch generation.",
        (
            "coding",
            "agents",
            "coding/execution/executor.py",
        ): "Lazy Hermes system-metrics integration for execution receipts.",
        (
            "logging_monitoring",
            "events",
            "logging_monitoring/handlers/event_bridge.py",
        ): "Optional logging-to-event-bus bridge isolated in a handler adapter.",
        (
            "orchestrator",
            "agents",
            "orchestrator/fractals/executor.py",
        ): "Fractal workflow adapter delegates leaf execution to the agent API.",
        (
            "orchestrator",
            "agents",
            "orchestrator/fractals/planner.py",
        ): "Fractal planning adapter delegates plan generation to the agent API.",
        (
            "orchestrator",
            "agents",
            "orchestrator/workflows/workflow_journal.py",
        ): "Optional workflow-journal persistence through the agent memory API.",
        (
            "orchestrator",
            "events",
            "orchestrator/execution/async_scheduler.py",
        ): "Lazy scheduler event emission through the typed event schema.",
        (
            "orchestrator",
            "events",
            "orchestrator/observability/orchestrator_events.py",
        ): "Dedicated orchestrator-to-event-bus observability adapter.",
        (
            "orchestrator",
            "utils",
            "orchestrator/core.py",
        ): "Shared CLI rendering helpers used by the orchestrator entry point.",
        (
            "orchestrator",
            "utils",
            "orchestrator/observability/reporting.py",
        ): "Shared CLI rendering helpers used by reporting.",
        (
            "orchestrator",
            "utils",
            "orchestrator/workflows/workflow_engine.py",
        ): "Shared deterministic topological-sort implementation.",
        (
            "security",
            "defense",
            "security/ai_safety/__init__.py",
        ): "Compatibility facade for the specialized active-defense API.",
        (
            "validation",
            "agents",
            "validation/pai.py",
        ): "PAI-specific validation adapter for agent request and result types.",
        (
            "validation",
            "utils",
            "validation/examples_validator.py",
        ): "Example-validation adapter uses the shared safe-subprocess utility.",
    }
)


def get_layer(module: str) -> str:
    """Determine the architectural layer of a module.

    Layers follow the hierarchy defined in SPEC.md:
    Foundation → Core → Service → Specialized
    """
    if module in FOUNDATION:
        return "foundation"
    if module in CORE:
        return "core"
    if module in SERVICE:
        return "service"
    if module in SPECIALIZED:
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
                edges.append(
                    {
                        "src": src_module,
                        "dst": dst_module,
                        "file": str(rel),
                        "src_layer": get_layer(src_module),
                        "dst_layer": get_layer(dst_module),
                    }
                )
    return edges


def _interface_contract_key(edge: Mapping[str, Any]) -> InterfaceContractKey:
    return (
        str(edge["src"]),
        str(edge["dst"]),
        str(edge["file"]).replace("\\", "/"),
    )


def get_upward_interface_contract(edge: Mapping[str, Any]) -> str | None:
    """Return the exact file-scoped contract for an import edge, if present."""

    return UPWARD_INTERFACE_CONTRACTS.get(_interface_contract_key(edge))


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

        if (
            src_rank is not None
            and dst_rank is not None
            and src_rank < dst_rank
            and get_upward_interface_contract(edge) is None
        ):
            reason = (
                f"{src_l.capitalize()} module '{edge['src']}' "
                f"imports {dst_l} module '{edge['dst']}'"
            )
            violations.append({**edge, "reason": reason})

    return violations


def audit_upward_interface_contracts(
    edges: list[dict[str, Any]],
    contracts: Mapping[InterfaceContractKey, str] = UPWARD_INTERFACE_CONTRACTS,
) -> dict[str, list[dict[str, str]]]:
    """Report used and stale exceptional upward-import contracts.

    A contract is used only when the exact source module, destination module,
    and repository-relative file still form an upward edge. Any unmatched
    registry entry is stale and should block the architecture audit.
    """

    upward_keys: set[InterfaceContractKey] = set()
    for edge in edges:
        ranks = {
            "foundation": 0,
            "core": 1,
            "service": 2,
            "specialized": 3,
        }
        src_rank = ranks.get(str(edge["src_layer"]))
        dst_rank = ranks.get(str(edge["dst_layer"]))
        if src_rank is not None and dst_rank is not None and src_rank < dst_rank:
            upward_keys.add(_interface_contract_key(edge))

    used: list[dict[str, str]] = []
    stale: list[dict[str, str]] = []
    for (src, dst, file_path), rationale in sorted(contracts.items()):
        record = {
            "src": src,
            "dst": dst,
            "file": file_path,
            "rationale": rationale,
        }
        if (src, dst, file_path) in upward_keys:
            used.append(record)
        else:
            stale.append(record)

    return {"used": used, "stale": stale}
