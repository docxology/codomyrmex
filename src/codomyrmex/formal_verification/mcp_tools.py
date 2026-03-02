"""MCP tool definitions for the formal_verification module.

Exposes the mcp-solver 6-tool interface as MCP tools that can be
discovered and invoked by Claude Code and other MCP-compatible agents.

References:
    - mcp-solver: https://github.com/szeider/mcp-solver
    - PAI Discussion #707: https://github.com/danielmiessler/Personal_AI_Infrastructure/discussions/707
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    # Fallback decorator if MCP module not available
    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        """mcp Tool ."""
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator

from .exceptions import BackendNotAvailableError, ModelBuildError
from .solver import ConstraintSolver

# Module-level solver instance for stateful MCP interactions
_solver: ConstraintSolver | None = None


def _get_solver() -> ConstraintSolver:
    """get Solver ."""
    global _solver
    if _solver is None:
        _solver = ConstraintSolver(backend="z3")
    return _solver


def _get_solver_safe() -> tuple[ConstraintSolver | None, dict[str, str] | None]:
    """Return (solver, None) on success, or (None, error_dict) on failure."""
    try:
        return _get_solver(), None
    except BackendNotAvailableError as exc:
        return None, {"status": "error", "error": str(exc)}


@mcp_tool(
    category="formal_verification",
    description="Remove all items from the constraint model, resetting to empty state.",
)
def clear_model() -> dict[str, str]:
    """Clear the entire constraint model."""
    solver, err = _get_solver_safe()
    if err:
        return err
    solver.clear_model()
    return {"status": "ok", "message": "Model cleared"}


@mcp_tool(
    category="formal_verification",
    description="Add a Z3 Python expression to the constraint model at an optional index.",
)
def add_item(item: str, index: int | None = None) -> dict[str, Any]:
    """Add an item (constraint/declaration) to the model.

    Args:
        item: Z3 Python code string (e.g., "x = Int('x')" or "solver.add(x > 0)").
        index: Optional position to insert at. Appends if None.
    """
    solver, err = _get_solver_safe()
    if err:
        return err
    idx = solver.add_item(item, index)
    return {"status": "ok", "index": idx, "item": item}


@mcp_tool(
    category="formal_verification",
    description="Delete the item at the specified index from the constraint model.",
)
def delete_item(index: int) -> dict[str, Any]:
    """Remove the item at the given index.

    Args:
        index: Zero-based index of the item to remove.
    """
    solver, err = _get_solver_safe()
    if err:
        return err
    try:
        removed = solver.delete_item(index)
    except ModelBuildError as exc:
        return {"status": "error", "error": str(exc)}
    return {"status": "ok", "removed_item": removed, "index": index}


@mcp_tool(
    category="formal_verification",
    description="Replace the item at the specified index with new content.",
)
def replace_item(index: int, new_item: str) -> dict[str, Any]:
    """Replace item at index.

    Args:
        index: Zero-based index of the item to replace.
        new_item: New Z3 Python code string.
    """
    solver, err = _get_solver_safe()
    if err:
        return err
    try:
        old = solver.replace_item(index, new_item)
    except ModelBuildError as exc:
        return {"status": "error", "error": str(exc)}
    return {"status": "ok", "old_item": old, "new_item": new_item, "index": index}


@mcp_tool(
    category="formal_verification",
    description="Retrieve the current constraint model as a numbered list of items.",
)
def get_model() -> dict[str, Any]:
    """Get the current model with numbered items."""
    solver, err = _get_solver_safe()
    if err:
        return err
    items = solver.get_model()
    return {
        "status": "ok",
        "item_count": len(items),
        "items": [{"index": idx, "content": content} for idx, content in items],
    }


@mcp_tool(
    category="formal_verification",
    description="Execute the Z3 solver on the current model with configurable timeout.",
)
def solve_model(timeout_ms: int = 30000) -> dict[str, Any]:
    """Solve the current constraint model.

    Args:
        timeout_ms: Maximum solving time in milliseconds (default 30000).
    """
    solver, err = _get_solver_safe()
    if err:
        return err
    result = solver.solve(timeout_ms)
    return {
        "status": result.status.value,
        "satisfiable": result.is_sat,
        "model": result.model,
        "objective_value": result.objective_value,
        "statistics": result.statistics,
        "error": result.error_message,
    }
