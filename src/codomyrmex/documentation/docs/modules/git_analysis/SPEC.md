# git_analysis -- Technical Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Git history and structural analysis module providing 16 MCP tools across two complementary analysis engines: GitNexus (Tree-sitter AST + KuzuDB knowledge graph) and GitPython (commit history analysis).

## Design Principles

- **Dual-engine**: Structural analysis (GitNexus) and temporal analysis (GitPython) are independent.
- **Graceful degradation**: GitNexus tools return error dicts when Node.js is unavailable.
- **Lazy instantiation**: Bridge and analyzer objects are created per-call via `_bridge()` and `_analyzer()`.
- **Input validation**: Numeric params clamped to `[1, 10000]` via `_validate_positive_int()`.

## Architecture

```
git_analysis/
  __init__.py                -- Exports GitHistoryAnalyzer, GitNexusBridge
  mcp_tools.py               -- 16 tool definitions (7 GitNexus + 9 GitPython)
  core/
    history_analyzer.py      -- GitHistoryAnalyzer (GitPython)
    gitnexus_bridge.py       -- GitNexusBridge (Node.js subprocess)
  vendor/gitnexus/           -- Vendored GitNexus source
```

## Functional Requirements

### GitNexus Tools (7)
- `git_analysis_index_repo(repo_path)` -- Index repository with Tree-sitter AST into KuzuDB.
- `git_analysis_query(repo_path, query_text, limit)` -- BM25 + semantic hybrid search.
- `git_analysis_symbol_context(repo_path, symbol)` -- 360-degree dependency graph for a symbol.
- `git_analysis_impact(repo_path, symbol)` -- Blast-radius assessment with confidence scoring.
- `git_analysis_detect_changes(repo_path, diff)` -- Map git diff to architectural impact.
- `git_analysis_cypher_query(repo_path, cypher_query)` -- Raw Cypher against KuzuDB.
- `git_analysis_list_indexed()` -- List all indexed repos in global registry.

### GitPython Tools (9)
- `git_analysis_commit_history(repo_path, max_count, branch)` -- Detailed commit history with stats.
- `git_analysis_contributor_stats(repo_path)` -- Per-author aggregated statistics.
- `git_analysis_code_churn(repo_path, top_n)` -- Top N most-changed files by frequency.
- `git_analysis_branch_topology(repo_path)` -- Branch names, tips, active branch.
- `git_analysis_commit_frequency(repo_path, by)` -- Commit frequency by day/week/month.
- `git_analysis_filtered_history(repo_path, max_count, since, until, author, branch)` -- Filtered commits.
- `git_analysis_file_history(repo_path, file_path, max_count)` -- Per-file commit history.
- `git_analysis_directory_churn(repo_path, top_n)` -- Churn by top-level directory.
- `git_analysis_hotspots(repo_path, top_n)` -- Hotspot analysis combining churn with recency.

## Interface Contracts

All tools return:
- Success: `{"status": "ok", ...}` with tool-specific keys (`commits`, `contributors`, `hotspots`, etc.)
- Failure: `{"status": "error", "error": "<message>"}`

## Dependencies

- **Internal**: `model_context_protocol.decorators` for `@mcp_tool`
- **External**: GitPython (core dependency)
- **External (optional)**: Node.js/npx for GitNexus bridge

## Constraints

- GitNexus requires prior indexing via `git_analysis_index_repo` before query/context/impact tools work.
- All tools are read-only; no repository modifications.
- Module version: `1.0.0` (internal).

## Navigation

- [Root](../../../../../../README.md)
