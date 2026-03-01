# git_analysis — Agent Context

## Module Summary

The `git_analysis` module provides two complementary capabilities for understanding codebases:

1. **GitPython history analysis** — commit history, contributors, code churn, branch topology
2. **GitNexus structural analysis** — symbol dependencies, blast radius, knowledge graph queries

Use this module when you need to *understand* a repository, not *operate* on it (use `git_operations` for that).

## Submodules

| Path | Purpose |
|------|---------|
| `core/__init__.py` | Re-exports `GitHistoryAnalyzer`, `GitNexusBridge`, `GitNexusNotAvailableError` |
| `core/history_analyzer.py` | `GitHistoryAnalyzer` — GitPython-based analysis (9 methods) |
| `core/gitnexus_bridge.py` | `GitNexusBridge` — Node.js subprocess bridge |
| `vendor/gitnexus/` | GitNexus git submodule (abhigyanpatwari/GitNexus) |
| `mcp_tools.py` | 16 MCP tools exposing both capabilities |
| `data/codomyrmex_description.md` | Live analysis output for the codomyrmex repo |

## Quick Reference for Agents

### When to use each tool

**Use GitPython tools when you need:**
- Recent commit history with stats → `git_analysis_commit_history`
- Top contributors for a repo → `git_analysis_contributor_stats`
- Files most likely to have bugs (high churn) → `git_analysis_code_churn`
- Current branch state → `git_analysis_branch_topology`
- Development velocity trends → `git_analysis_commit_frequency`
- Commits in a date range or by a specific author → `git_analysis_filtered_history`
- History of a specific file → `git_analysis_file_history`
- Module-level activity breakdown → `git_analysis_directory_churn`
- High-risk files combining churn and recency → `git_analysis_hotspots`

**Use GitNexus tools when you need:**
- To find all callers of a function → `git_analysis_symbol_context`
- Blast radius before refactoring → `git_analysis_impact`
- Semantic code search → `git_analysis_query`
- Architectural impact of a PR → `git_analysis_detect_changes`

### GitNexus workflow

GitNexus requires indexing before queries:
```
1. git_analysis_index_repo(repo_path=".") → creates .gitnexus/ graph
2. git_analysis_query(repo_path=".", query_text="my question")
   OR git_analysis_impact(repo_path=".", symbol="ClassName")
```

### Availability check

```python
from codomyrmex.git_analysis import GITNEXUS_AVAILABLE
# GITNEXUS_AVAILABLE = True if npx/node is on PATH
```

Always check before using GitNexus tools in automation:
```python
result = git_analysis_index_repo(repo_path=".")
if result["status"] == "error":
    # GitNexus unavailable — fall back to GitPython tools
    pass
```

## Codomyrmex Self-Description

Pre-computed analysis of this repository is at `data/codomyrmex_description.md`.
Key findings:
- 4 contributors (Daniel Ari Friedman: 124 commits, NewTester: 110 commits)
- Peak activity: February 2026 (144 commits)
- Highest churn: README.md (58x), TO-DO.md (46x), pyproject.toml (42x)
- 2 branches: main (active), pr3-branch

## MCP Tools Available

All 16 tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

### GitNexus Tools (structural code analysis -- requires Node.js/npx)

| Tool | Description | Key Parameters | Trust Level |
|------|-------------|----------------|-------------|
| `git_analysis_index_repo` | Index a repository with GitNexus (Tree-sitter AST + KuzuDB graph) | `repo_path` | Safe |
| `git_analysis_query` | Hybrid BM25 + semantic search over the GitNexus knowledge graph | `repo_path`, `query_text`, `limit` | Safe |
| `git_analysis_symbol_context` | 360-degree symbol analysis: all incoming and outgoing dependencies | `repo_path`, `symbol` | Safe |
| `git_analysis_impact` | Blast-radius assessment for a symbol change with confidence scoring | `repo_path`, `symbol` | Safe |
| `git_analysis_detect_changes` | Map a git diff to architectural impact on modules and symbols | `repo_path`, `diff` (optional) | Safe |
| `git_analysis_cypher_query` | Execute a raw Cypher query against the KuzuDB knowledge graph | `repo_path`, `cypher_query` | Safe |
| `git_analysis_list_indexed` | List all repositories indexed in the global GitNexus registry | (none) | Safe |

### GitPython Tools (commit history analysis)

| Tool | Description | Key Parameters | Trust Level |
|------|-------------|----------------|-------------|
| `git_analysis_commit_history` | Detailed commit history with per-commit statistics | `repo_path`, `max_count`, `branch` | Safe |
| `git_analysis_contributor_stats` | Per-author aggregate statistics across all commits | `repo_path` | Safe |
| `git_analysis_code_churn` | Top N most-frequently-changed files (code churn analysis) | `repo_path`, `top_n` | Safe |
| `git_analysis_branch_topology` | Repository branch topology: all branches and tip commits | `repo_path` | Safe |
| `git_analysis_commit_frequency` | Commit frequency bucketed by day, week, or month | `repo_path`, `by` (day/week/month) | Safe |
| `git_analysis_filtered_history` | Filtered commit history with date, author, and branch constraints | `repo_path`, `max_count`, `since`, `until`, `author`, `branch` | Safe |
| `git_analysis_file_history` | Commit history for a specific file path | `repo_path`, `file_path`, `max_count` | Safe |
| `git_analysis_directory_churn` | Commit frequency aggregated by top-level directory | `repo_path`, `top_n` | Safe |
| `git_analysis_hotspots` | Hotspot analysis combining churn frequency with recency | `repo_path`, `top_n` | Safe |

## Testing

Tests at `src/codomyrmex/tests/unit/git_analysis/`:
- `test_history_analyzer.py` — 27 tests against actual codomyrmex repo
- `test_gitnexus_bridge.py` — 9 tests, Node.js tests skipif-guarded
- `test_mcp_tools.py` — 27 tests covering all 16 MCP tools

Run: `uv run pytest src/codomyrmex/tests/unit/git_analysis/ -v`
Expected: 63 tests pass (Node.js integration test may be skipped if unavailable)

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `git_operations` | Sibling — operational vs. analytical. git_analysis depends on GitPython same as git_operations does. |
| `model_context_protocol` | Used for `@mcp_tool` decorator registration |
| `logging_monitoring` | Used for structured logging (Foundation Layer) |
| `formal_verification` | Parallel pattern — both have `vendor/` git submodules |
