"""Module dependency DAG exporter as Mermaid diagrams.

Scans ``src/codomyrmex/`` to build a module-level import graph and
renders it as a Mermaid flowchart.

Example::

    dag = build_module_dag()
    mermaid_text = render_dag_mermaid(dag)
    print(mermaid_text)
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SRC_ROOT = _REPO_ROOT / "src" / "codomyrmex"


@dataclass
class ModuleNode:
    """A node in the module dependency graph.

    Attributes:
        name: Module name (e.g., ``"auth"``).
        file_count: Number of ``.py`` files in the module.
        loc: Total lines of code.
        imports: Set of module names this module imports from.
    """

    name: str
    file_count: int = 0
    loc: int = 0
    imports: set[str] = field(default_factory=set)


@dataclass
class ModuleDAG:
    """A directed acyclic graph of module dependencies.

    Attributes:
        nodes: Mapping of module name to :class:`ModuleNode`.
        edge_count: Total number of dependency edges.
    """

    nodes: dict[str, ModuleNode] = field(default_factory=dict)

    @property
    def edge_count(self) -> int:
        """Total number of dependency edges."""
        return sum(len(n.imports) for n in self.nodes.values())


def _extract_imports(filepath: Path, known_modules: set[str]) -> set[str]:
    """Extract codomyrmex module imports from a Python file."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            parts = node.module.split(".")
            # Match "codomyrmex.X" or "from .X import ..."
            if len(parts) >= 2 and parts[0] == "codomyrmex":
                mod = parts[1]
                if mod in known_modules:
                    imports.add(mod)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if len(parts) >= 2 and parts[0] == "codomyrmex":
                    mod = parts[1]
                    if mod in known_modules:
                        imports.add(mod)
    return imports


def build_module_dag(src_root: Path | None = None) -> ModuleDAG:
    """Build a module dependency DAG by scanning source imports.

    Args:
        src_root: Root of the ``codomyrmex`` source tree.
                  Defaults to ``src/codomyrmex/``.

    Returns:
        A :class:`ModuleDAG` with nodes and edges.
    """
    root = src_root or _SRC_ROOT
    dag = ModuleDAG()

    # Discover modules (top-level directories with __init__.py)
    module_dirs = sorted(
        d
        for d in root.iterdir()
        if d.is_dir()
        and (d / "__init__.py").exists()
        and not d.name.startswith("_")
        and d.name != "tests"
    )
    known = {d.name for d in module_dirs}

    for mod_dir in module_dirs:
        py_files = [
            f
            for f in mod_dir.rglob("*.py")
            if "__pycache__" not in str(f)
        ]
        loc = sum(
            len(f.read_text(encoding="utf-8", errors="replace").splitlines())
            for f in py_files
        )
        node = ModuleNode(name=mod_dir.name, file_count=len(py_files), loc=loc)

        for pyf in py_files:
            imported = _extract_imports(pyf, known)
            imported.discard(mod_dir.name)  # remove self-imports
            node.imports.update(imported)

        dag.nodes[mod_dir.name] = node

    logger.info(
        "Built module DAG: %d nodes, %d edges",
        len(dag.nodes),
        dag.edge_count,
    )
    return dag


def _classify_module(name: str) -> str:
    """Return a Mermaid style class for the module layer."""
    foundation = {"logging_monitoring", "environment_setup", "model_context_protocol", "terminal_interface", "exceptions"}
    core = {"agents", "static_analysis", "coding", "data_visualization", "search", "git_operations", "security", "llm", "performance", "git_analysis"}
    service = {"deployment", "documentation", "api", "ci_cd_automation", "containerization", "database_management", "orchestrator", "config_management", "website"}
    if name in foundation:
        return "foundation"
    if name in core:
        return "core"
    if name in service:
        return "service"
    return "specialized"


def render_dag_mermaid(
    dag: ModuleDAG,
    *,
    direction: str = "LR",
    max_edges: int = 200,
    min_imports: int = 0,
) -> str:
    """Render the DAG as a Mermaid flowchart.

    Args:
        dag: The module dependency graph.
        direction: Flowchart direction (``"LR"``, ``"TB"``, etc.).
        max_edges: Maximum edges to render (prune smallest modules first).
        min_imports: Only show modules with at least this many imports.

    Returns:
        Mermaid diagram source string.
    """
    lines: list[str] = [f"flowchart {direction}"]

    # Style classes
    lines.append("    classDef foundation fill:#eff6ff,stroke:#3b82f6,color:#1e40af")
    lines.append("    classDef core fill:#f0fdf4,stroke:#22c55e,color:#166534")
    lines.append("    classDef service fill:#fefce8,stroke:#eab308,color:#854d0e")
    lines.append("    classDef specialized fill:#fdf2f8,stroke:#ec4899,color:#9d174d")

    # Nodes
    filtered = {
        name: node
        for name, node in dag.nodes.items()
        if len(node.imports) >= min_imports or any(
            name in other.imports for other in dag.nodes.values()
        )
    }

    for name, node in sorted(filtered.items()):
        label = f"{name}\\n{node.file_count}f / {node.loc}L"
        layer = _classify_module(name)
        lines.append(f'    {name}["{label}"]:::{layer}')

    # Edges (capped)
    edges: list[tuple[str, str]] = []
    for name, node in sorted(filtered.items()):
        for imp in sorted(node.imports):
            if imp in filtered:
                edges.append((name, imp))

    for src, dst in edges[:max_edges]:
        lines.append(f"    {src} --> {dst}")

    return "\n".join(lines)


def export_dag_file(
    output_path: Path | str,
    src_root: Path | None = None,
    **render_kwargs: object,
) -> Path:
    """Build and save the module DAG as a Mermaid file.

    Args:
        output_path: Destination ``.mmd`` file path.
        src_root: Source root for scanning.
        **render_kwargs: Passed to :func:`render_dag_mermaid`.

    Returns:
        The written file path.
    """
    dag = build_module_dag(src_root)
    mermaid_text = render_dag_mermaid(dag, **render_kwargs)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(mermaid_text, encoding="utf-8")
    logger.info("Exported DAG to %s (%d nodes)", out, len(dag.nodes))
    return out


__all__ = [
    "ModuleDAG",
    "ModuleNode",
    "build_module_dag",
    "export_dag_file",
    "render_dag_mermaid",
]
