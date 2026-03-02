"""Solver backend abstraction layer.

Supports multiple constraint-solving backends following mcp-solver's
multi-backend architecture. Z3 is the primary backend; others can be
added by subclassing SolverBackend.
"""

from .base import SolverBackend, SolverResult, SolverStatus
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

__all__ = ["SolverBackend", "SolverResult", "SolverStatus"]

# Lazy import of Z3 backend to avoid hard dependency
try:
    from .z3_backend import Z3Backend
    __all__.append("Z3Backend")
except ImportError as e:
    logger.debug("Z3 backend not available (z3-solver not installed): %s", e)
    pass
