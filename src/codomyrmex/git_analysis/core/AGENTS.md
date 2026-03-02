# Core - Agent Coordination

## Purpose

Git repository analysis engine combining GitPython-based commit history analysis with GitNexus structural code analysis via subprocess bridge.

## Key Components

| Component | Role |
|-----------|------|
| `GitHistoryAnalyzer` | Commit history, contributor stats, churn, hotspot, and frequency analysis via GitPython |
| `GitNexusBridge` | Subprocess bridge to GitNexus Node.js CLI for structural code queries |
| `GitNexusNotAvailableError` | Raised when neither npx nor vendor GitNexus is found |

## Operating Contracts

- `GitHistoryAnalyzer` operates on the git object model directly (no subprocess calls). Requires a valid git repository path.
- `GitNexusBridge` requires Node.js/npx or a built vendor distribution. Call `check_availability()` before use.
- `GitNexusBridge.analyze()` must be called before `query()`, `get_context()`, or `assess_impact()` -- it indexes the repository.
- `max_count` parameters are capped at 10000 to prevent memory exhaustion.
- History analyzer complements git_operations (operational) with analytical capabilities (read-only).

## Integration Points

- **Parent module**: `git_analysis/` exposes 16 `@mcp_tool`-decorated tools via `mcp_tools.py`.
- **GitPython**: Core dependency -- no extra install required.
- **GitNexus**: Optional Node.js tool for Tree-sitter AST + KuzuDB graph analysis.

## Navigation

- **Parent**: [git_analysis/](../README.md)
- **Sibling**: [SPEC.md](SPEC.md)
- **Root**: [/README.md](../../../../README.md)
