"""MCP tool definitions for the git_analysis module.

Exposes 16 tools in two groups:
  - 7 GitNexus tools: structural code analysis (requires Node.js/npx)
  - 9 GitPython tools: commit history, contributors, churn, topology,
    filtered history, file history, directory churn, hotspots

All tools return {"status": "ok", ...} on success or
{"status": "error", "error": "<message>"} on failure.

GitNexus tools gracefully return an error dict when Node.js is unavailable
rather than raising exceptions, enabling mixed environments.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator


def _validate_positive_int(name: str, value: int, default: int) -> int:
    """Clamp to [1, 10000]. Raises ValueError if value < 1."""
    if value < 1:
        raise ValueError(f"{name} must be >= 1, got {value}")
    return min(value, 10000)


def _bridge(repo_path: str):
    """Lazy import + instantiation of GitNexusBridge."""
    from .core.gitnexus_bridge import GitNexusBridge
    return GitNexusBridge(repo_path)


def _analyzer(repo_path: str):
    """Lazy import + instantiation of GitHistoryAnalyzer."""
    from .core.history_analyzer import GitHistoryAnalyzer
    return GitHistoryAnalyzer(repo_path)


# ── GitNexus Tools (structural code analysis) ──────────────────────────────


@mcp_tool(
    category="git_analysis",
    description=(
        "Index a repository with GitNexus (Tree-sitter AST + KuzuDB graph). "
        "Must be run before query/context/impact tools. Requires Node.js/npx."
    ),
)
def git_analysis_index_repo(repo_path: str) -> dict[str, Any]:
    """Index a repository with GitNexus for structural analysis."""
    try:
        b = _bridge(repo_path)
        if not b.check_availability():
            return {
                "status": "error",
                "error": "GitNexus not available. Install Node.js or npx.",
            }
        result = b.analyze()
        return {"status": "ok", "repo_path": repo_path, "result": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "Hybrid BM25 + semantic search over the GitNexus knowledge graph. "
        "Finds symbols, files, and concepts matching a natural-language query."
    ),
)
def git_analysis_query(
    repo_path: str, query_text: str, limit: int = 10
) -> dict[str, Any]:
    """Search the GitNexus knowledge graph with a natural-language query."""
    try:
        limit = _validate_positive_int("limit", limit, 10)
        b = _bridge(repo_path)
        if not b.check_availability():
            return {
                "status": "error",
                "error": "GitNexus not available. Install Node.js or npx.",
            }
        result = b.query(query_text, limit=limit)
        return {"status": "ok", "query": query_text, "results": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "360-degree symbol analysis: all incoming and outgoing dependencies "
        "for a given symbol. Returns callers, callees, and transitive graph."
    ),
)
def git_analysis_symbol_context(repo_path: str, symbol: str) -> dict[str, Any]:
    """Get full dependency context for a symbol from the knowledge graph."""
    try:
        b = _bridge(repo_path)
        if not b.check_availability():
            return {
                "status": "error",
                "error": "GitNexus not available. Install Node.js or npx.",
            }
        result = b.get_context(symbol)
        return {"status": "ok", "symbol": symbol, "context": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "Blast-radius assessment for a symbol change. Returns all symbols "
        "transitively affected with confidence scoring."
    ),
)
def git_analysis_impact(repo_path: str, symbol: str) -> dict[str, Any]:
    """Assess the blast radius if a given symbol is changed or removed."""
    try:
        b = _bridge(repo_path)
        if not b.check_availability():
            return {
                "status": "error",
                "error": "GitNexus not available. Install Node.js or npx.",
            }
        result = b.assess_impact(symbol)
        return {"status": "ok", "symbol": symbol, "impact": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "Map a git diff to architectural impact. Shows which modules and "
        "symbols are affected by staged or provided changes."
    ),
)
def git_analysis_detect_changes(
    repo_path: str, diff: str | None = None
) -> dict[str, Any]:
    """Map git diff to architectural impact using the knowledge graph."""
    try:
        b = _bridge(repo_path)
        if not b.check_availability():
            return {
                "status": "error",
                "error": "GitNexus not available. Install Node.js or npx.",
            }
        result = b.detect_changes(diff=diff)
        return {"status": "ok", "impact": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "Execute a raw Cypher query against the KuzuDB knowledge graph. "
        "For advanced graph traversal beyond the built-in query tools."
    ),
)
def git_analysis_cypher_query(repo_path: str, cypher_query: str) -> dict[str, Any]:
    """Run a raw Cypher query against the GitNexus KuzuDB graph."""
    try:
        b = _bridge(repo_path)
        if not b.check_availability():
            return {
                "status": "error",
                "error": "GitNexus not available. Install Node.js or npx.",
            }
        result = b.run_cypher(cypher_query)
        return {"status": "ok", "query": cypher_query, "result": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "List all repositories indexed in the global GitNexus registry "
        "(~/.gitnexus). Shows previously analyzed repos."
    ),
)
def git_analysis_list_indexed() -> dict[str, Any]:
    """List all repositories in the global GitNexus registry."""
    try:
        # Use "." as dummy path — list-repos is global, not repo-specific
        b = _bridge(".")
        if not b.check_availability():
            return {
                "status": "error",
                "error": "GitNexus not available. Install Node.js or npx.",
            }
        repos = b.list_repos()
        return {"status": "ok", "repos": repos, "count": len(repos)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


# ── GitPython Tools (commit history analysis) ───────────────────────────────


@mcp_tool(
    category="git_analysis",
    description=(
        "Detailed commit history with per-commit statistics: insertions, "
        "deletions, files changed. Walks a branch from newest to oldest."
    ),
)
def git_analysis_commit_history(
    repo_path: str = ".", max_count: int = 50, branch: str | None = None
) -> dict[str, Any]:
    """Get detailed commit history with stats for a repository."""
    try:
        max_count = _validate_positive_int("max_count", max_count, 50)
        result = _analyzer(repo_path).get_commit_history(
            max_count=max_count, branch=branch
        )
        return {"status": "ok", "commits": result, "count": len(result)}
    except ValueError as exc:
        return {"status": "error", "error": str(exc)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "Per-author aggregate statistics across all commits: total commits, "
        "insertions, deletions, first and last contribution dates."
    ),
)
def git_analysis_contributor_stats(repo_path: str = ".") -> dict[str, Any]:
    """Get per-contributor aggregate statistics across the full git history."""
    try:
        result = _analyzer(repo_path).get_contributor_stats()
        return {"status": "ok", "contributors": result, "count": len(result)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "Top N most-frequently-changed files (code churn analysis). "
        "High-churn files indicate instability or need for refactoring."
    ),
)
def git_analysis_code_churn(repo_path: str = ".", top_n: int = 20) -> dict[str, Any]:
    """Identify the most-changed files by commit frequency (code churn)."""
    try:
        top_n = _validate_positive_int("top_n", top_n, 20)
        result = _analyzer(repo_path).get_code_churn(top_n=top_n)
        return {"status": "ok", "files": result, "count": len(result)}
    except ValueError as exc:
        return {"status": "error", "error": str(exc)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "Repository branch topology: all branches, their tip commits, "
        "and the currently active branch."
    ),
)
def git_analysis_branch_topology(repo_path: str = ".") -> dict[str, Any]:
    """Get branch names, tip commits, and active branch for a repository."""
    try:
        result = _analyzer(repo_path).get_branch_topology()
        return {"status": "ok", **result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "Commit frequency bucketed by day, week, or month. "
        "Reveals development velocity and activity patterns over time."
    ),
)
def git_analysis_commit_frequency(
    repo_path: str = ".", by: str = "week"
) -> dict[str, Any]:
    """Get commit frequency bucketed by time period (day/week/month)."""
    if by not in {"day", "week", "month"}:
        return {"status": "error", "error": f"by must be one of 'day', 'week', 'month', got {by!r}"}
    try:
        result = _analyzer(repo_path).get_commit_frequency(by=by)
        return {"status": "ok", "frequency": result, "bucket": by}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "Filtered commit history with optional since/until date, author, "
        "and branch constraints. Dates in ISO-8601 format."
    ),
)
def git_analysis_filtered_history(
    repo_path: str = ".",
    max_count: int = 50,
    since: str | None = None,
    until: str | None = None,
    author: str | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    """Get filtered commit history with date/author constraints."""
    try:
        max_count = _validate_positive_int("max_count", max_count, 50)
        result = _analyzer(repo_path).get_commit_history_filtered(
            max_count=max_count, since=since, until=until, author=author, branch=branch
        )
        return {"status": "ok", "commits": result, "count": len(result)}
    except ValueError as exc:
        return {"status": "error", "error": str(exc)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "Commit history for a specific file path. "
        "Shows every commit that touched the file."
    ),
)
def git_analysis_file_history(
    repo_path: str = ".", file_path: str = "", max_count: int = 50
) -> dict[str, Any]:
    """Get commit history for a specific file."""
    try:
        max_count = _validate_positive_int("max_count", max_count, 50)
        result = _analyzer(repo_path).get_file_history(file_path=file_path, max_count=max_count)
        return {"status": "ok", "file": file_path, "commits": result, "count": len(result)}
    except ValueError as exc:
        return {"status": "error", "error": str(exc)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "Commit frequency aggregated by top-level directory. "
        "Identifies which modules have the most git activity."
    ),
)
def git_analysis_directory_churn(
    repo_path: str = ".", top_n: int = 10
) -> dict[str, Any]:
    """Get commit churn aggregated by top-level directory."""
    try:
        top_n = _validate_positive_int("top_n", top_n, 10)
        result = _analyzer(repo_path).get_churn_by_directory(top_n=top_n)
        return {"status": "ok", "directories": result, "count": len(result)}
    except ValueError as exc:
        return {"status": "error", "error": str(exc)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_analysis",
    description=(
        "Hotspot analysis combining churn frequency with recency. "
        "High-score files are both frequently changed and recently touched."
    ),
)
def git_analysis_hotspots(
    repo_path: str = ".", top_n: int = 20
) -> dict[str, Any]:
    """Identify high-risk hotspot files by churn and recency."""
    try:
        top_n = _validate_positive_int("top_n", top_n, 20)
        result = _analyzer(repo_path).get_hotspot_analysis(top_n=top_n)
        return {"status": "ok", "hotspots": result, "count": len(result)}
    except ValueError as exc:
        return {"status": "error", "error": str(exc)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
