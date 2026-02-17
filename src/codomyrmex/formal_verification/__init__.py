"""Codomyrmex Formal Verification Module — constraint solving via Z3/SMT.

Integrates constraint solving capabilities into the Codomyrmex platform,
inspired by szeider/mcp-solver and proposed in PAI Discussion #707 by Spirotot.

Provides:
    - Z3 SMT solver backend with mcp-solver 6-tool interface
    - PAI Algorithm ISC criteria consistency verification
    - MCP tools for Claude Code integration
    - Extensible backend architecture for SAT/MaxSAT/ASP solvers

Submodules:
    backends    — Pluggable solver backend implementations (Z3 primary)
    solver      — High-level ConstraintSolver API
    mcp_tools   — MCP tool definitions for agent integration
    verify_isc  — PAI Algorithm ISC constraint verification bridge

References:
    - Z3 Prover: https://github.com/Z3Prover/z3
    - mcp-solver: https://github.com/szeider/mcp-solver
    - PAI Discussion: https://github.com/danielmiessler/Personal_AI_Infrastructure/discussions/707
"""

__version__ = "0.1.0"

from .exceptions import (
    BackendNotAvailableError,
    InvalidConstraintError,
    ModelBuildError,
    SolverError,
    SolverTimeoutError,
    UnsatisfiableError,
)
from .solver import ConstraintSolver
from .verify_isc import ISCVerificationResult, verify_criteria_consistency

# Lazy imports for optional backends
from .backends.base import SolverBackend, SolverResult, SolverStatus

__all__ = [
    "__version__",
    # Core API
    "ConstraintSolver",
    "verify_criteria_consistency",
    "ISCVerificationResult",
    # Backend abstractions
    "SolverBackend",
    "SolverResult",
    "SolverStatus",
    # Exceptions
    "SolverError",
    "SolverTimeoutError",
    "ModelBuildError",
    "UnsatisfiableError",
    "BackendNotAvailableError",
    "InvalidConstraintError",
]


def cli_commands():
    """Return CLI commands for the formal_verification module."""
    return {
        "solver:status": _cmd_status,
        "solver:backends": _cmd_backends,
        "solver:check": _cmd_check,
    }


def _cmd_status(**kwargs):
    """Show solver availability."""
    results = {"z3_available": False, "version": __version__}
    try:
        import z3
        results["z3_available"] = True
        results["z3_version"] = z3.get_version_string()
    except ImportError:
        results["z3_version"] = "not installed"
    return results


def _cmd_backends(**kwargs):
    """List available solver backends."""
    backends = []
    try:
        from .backends.z3_backend import Z3Backend
        backends.append({"name": "z3", "status": "available", "description": "Z3 SMT Solver"})
    except ImportError:
        backends.append({"name": "z3", "status": "unavailable", "description": "Install: pip install z3-solver"})
    return {"backends": backends}


def _cmd_check(expression: str = "", **kwargs):
    """Quick satisfiability check on a Z3 expression."""
    if not expression:
        return {"error": "Provide an expression to check"}
    try:
        solver = ConstraintSolver()
        solver.add_item(expression)
        result = solver.solve(timeout_ms=5000)
        return {"expression": expression, "status": result.status.value, "model": result.model}
    except Exception as exc:
        return {"expression": expression, "error": str(exc)}
