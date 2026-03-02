# Core - Technical Specification

## Overview

Two complementary analysis engines: `GitHistoryAnalyzer` for commit history analytics via GitPython, and `GitNexusBridge` for structural code analysis via the GitNexus Node.js CLI.

## Key Classes

### `GitHistoryAnalyzer` (history_analyzer.py)

All methods return `list[dict]` or `dict` -- no custom return types.

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_commit_history` | `max_count: int = 50`, `branch: str \| None` | `list[dict]` (sha, author, email, date, message, insertions, deletions, files_changed) |
| `get_contributor_stats` | none | `list[dict]` sorted by commit count desc |
| `get_code_churn` | `top_n: int = 20` | `list[dict]` (file, change_count) |
| `get_branch_topology` | none | `dict` (active_branch, branches list, branch_count) |
| `get_commit_frequency` | `by: str = "week"` | `dict[str, int]` period-to-count mapping |
| `get_commit_history_filtered` | `max_count`, `since`, `until`, `author`, `branch` | `list[dict]` with date/author filters |
| `get_file_history` | `file_path: str`, `max_count: int = 50` | `list[dict]` commits touching a specific file |
| `get_churn_by_directory` | `top_n: int = 10` | `list[dict]` (directory, change_count, files) |
| `get_hotspot_analysis` | `top_n: int = 20` | `list[dict]` with hotspot_score = churn / (1 + days_ago/30) |

### `GitNexusBridge` (gitnexus_bridge.py)

Subprocess-based bridge. Prefers `npx gitnexus`, falls back to `vendor/gitnexus/dist/index.js`.

| Method | Parameters | Returns |
|--------|-----------|---------|
| `check_availability` | none | `bool` |
| `analyze` | none | `dict` (stdout, stderr, indexed) -- indexes repo |
| `query` | `query_text: str`, `limit: int = 10` | `dict` -- hybrid BM25 + semantic search |
| `get_context` | `symbol: str` | `dict` -- 360-degree dependency analysis |
| `assess_impact` | `symbol: str` | `dict` -- blast-radius assessment |
| `detect_changes` | `diff: str \| None` | `dict` -- maps diff to architectural impact |
| `run_cypher` | `cypher_query: str` | `dict` -- raw KuzuDB Cypher query |
| `list_repos` | none | `list[dict]` -- all indexed repos |

## Dependencies

- **Internal**: `logging`
- **External**: `gitpython` (core dep), `Node.js/npx` (optional, for GitNexus)

## Constraints

- `max_count` values capped at 10000 via `min(max(1, max_count), 10000)`.
- GitNexus subprocess calls default to 60s timeout (300s for `analyze()`).
- All GitHistoryAnalyzer methods are read-only -- no repository modifications.

## Error Handling

| Error | Trigger |
|-------|---------|
| `GitNexusNotAvailableError` | Neither npx nor vendor GitNexus found |
| `RuntimeError` | GitNexus CLI returns non-zero exit code |
| `git.InvalidGitRepositoryError` | Invalid repo path passed to GitHistoryAnalyzer |
