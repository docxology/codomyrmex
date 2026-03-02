"""MCP tools for the static_analysis module.

Exposes static analysis capabilities — export auditing, dead export detection,
and full audit reports — via the PAI MCP bridge.
"""

from __future__ import annotations

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs):  # type: ignore[misc]
        def decorator(fn):
            fn._mcp_tool_meta = kwargs
            return fn
        return decorator


@mcp_tool(
    category="static_analysis",
    description=(
        "Audit all modules under a source directory for missing __all__ definitions. "
        "Returns a list of findings, each with module name and issue detail."
    ),
)
def static_analysis_audit_exports(src_dir: str) -> list[dict]:
    """Return modules missing __all__ definitions under *src_dir*.

    Args:
        src_dir: Path to the source directory to scan (e.g. ``'src/codomyrmex'``).

    Returns:
        List of dicts, each with ``module``, ``issue``, and ``detail`` keys.
    """
    from pathlib import Path

    from codomyrmex.static_analysis.exports import audit_exports

    return audit_exports(Path(src_dir))


@mcp_tool(
    category="static_analysis",
    description=(
        "Find exports listed in __all__ that are never imported anywhere in the codebase. "
        "Returns a list of dead exports with module, export_name, and detail."
    ),
)
def static_analysis_find_dead_exports(src_dir: str) -> list[dict]:
    """Return __all__ entries never imported elsewhere under *src_dir*.

    Args:
        src_dir: Path to the source directory to scan.

    Returns:
        List of dicts with ``module``, ``export_name``, and ``detail`` keys.
    """
    from pathlib import Path

    from codomyrmex.static_analysis.exports import find_dead_exports

    return find_dead_exports(Path(src_dir))


@mcp_tool(
    category="static_analysis",
    description=(
        "Run all static analysis audits (missing __all__, dead exports, unused functions) "
        "on a source directory. Returns a unified report dict with summary counts."
    ),
)
def static_analysis_full_audit(src_dir: str) -> dict:
    """Run the full static analysis audit suite on *src_dir*.

    Args:
        src_dir: Path to the source directory to audit.

    Returns:
        Dict with keys ``missing_all``, ``dead_exports``, ``unused_functions``,
        and ``summary`` (containing counts for each category).
    """
    from pathlib import Path

    from codomyrmex.static_analysis.exports import full_audit

    return full_audit(Path(src_dir))
