# git_analysis - Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides 16 MCP tools across two groups: 7 GitNexus tools for structural code analysis (requires Node.js/npx) and 9 GitPython tools for commit history analysis. GitNexus tools gracefully return error dicts when Node.js is unavailable.

## Key Files

| File | Role |
|------|------|
| `__init__.py` | Package root; exports `GitHistoryAnalyzer`, `GitNexusBridge` |
| `mcp_tools.py` | 16 MCP tool definitions |
| `core/history_analyzer.py` | `GitHistoryAnalyzer` (commit history, contributors, churn, topology) |
| `core/gitnexus_bridge.py` | `GitNexusBridge` (structural analysis via Node.js subprocess) |

## MCP Tools Available

**GitNexus tools (require Node.js):**

| Tool | Key Parameters |
|------|---------------|
| `git_analysis_index_repo` | `repo_path: str` |
| `git_analysis_query` | `repo_path: str, query_text: str, limit: int` |
| `git_analysis_symbol_context` | `repo_path: str, symbol: str` |
| `git_analysis_impact` | `repo_path: str, symbol: str` |
| `git_analysis_detect_changes` | `repo_path: str, diff: str (optional)` |
| `git_analysis_cypher_query` | `repo_path: str, cypher_query: str` |
| `git_analysis_list_indexed` | none |

**GitPython tools:**

| Tool | Key Parameters |
|------|---------------|
| `git_analysis_commit_history` | `repo_path: str, max_count: int, branch: str` |
| `git_analysis_contributor_stats` | `repo_path: str` |
| `git_analysis_code_churn` | `repo_path: str, top_n: int` |
| `git_analysis_branch_topology` | `repo_path: str` |
| `git_analysis_commit_frequency` | `repo_path: str, by: str (day/week/month)` |
| `git_analysis_filtered_history` | `repo_path: str, max_count: int, since/until/author/branch` |
| `git_analysis_file_history` | `repo_path: str, file_path: str, max_count: int` |
| `git_analysis_directory_churn` | `repo_path: str, top_n: int` |
| `git_analysis_hotspots` | `repo_path: str, top_n: int` |

## Agent Instructions

1. GitNexus tools require `git_analysis_index_repo` to be run first before query/context/impact tools.
2. GitPython tools work on any valid git repository without prior indexing.
3. The `by` parameter for `git_analysis_commit_frequency` must be one of `"day"`, `"week"`, or `"month"`.
4. Numeric parameters (`max_count`, `top_n`, `limit`) are clamped to `[1, 10000]`.
5. All tools return `{"status": "ok", ...}` on success or `{"status": "error", "error": "..."}` on failure.

## Operating Contracts

- GitNexus tools return error dicts (not exceptions) when Node.js is unavailable.
- `repo_path` defaults to `"."` for GitPython tools.
- All tools are read-only and do not modify the repository.

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Primary Tools |
|-----------|-------------|---------------|
| Engineer | Full | All 16 tools |
| Architect | Full | Impact, symbol context, architecture tools |
| QATester | Read | Commit history, churn, hotspots |

## Navigation

- [Root](../../../../../../README.md)
