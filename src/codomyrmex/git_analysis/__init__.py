"""Git analysis module for Codomyrmex.

Provides two complementary capabilities:

  - **GitNexus bridge**: structural code analysis via knowledge graph
    (requires Node.js/npx; vendored at vendor/gitnexus/)
    → symbol dependencies, call chains, blast-radius assessment

  - **Git history analysis**: commit history, contributors, code churn,
    branch topology (via GitPython — a core dependency)
    → commit frequency, contributor stats, high-churn file detection

Both capabilities are exposed as MCP tools in mcp_tools.py (16 total).
"""

from __future__ import annotations

from .core.history_analyzer import GitHistoryAnalyzer

try:
    from .core.gitnexus_bridge import GitNexusBridge, GitNexusNotAvailableError
    GITNEXUS_AVAILABLE = True
except ImportError:
    GITNEXUS_AVAILABLE = False

__all__ = ["GitHistoryAnalyzer", "GITNEXUS_AVAILABLE"]
if GITNEXUS_AVAILABLE:
    __all__ += ["GitNexusBridge", "GitNexusNotAvailableError"]

__version__ = "1.0.0"
