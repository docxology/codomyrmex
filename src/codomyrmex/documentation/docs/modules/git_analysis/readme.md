# git_analysis

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Git history analysis module providing two complementary capabilities. The **GitNexus bridge** performs structural code analysis via a Tree-sitter AST and KuzuDB knowledge graph (requires Node.js/npx). The **GitPython history analyzer** provides commit history, contributor statistics, code churn, branch topology, and hotspot detection using GitPython.

Both capabilities are exposed as 16 MCP tools.

## PAI Integration

| PAI Phase | Capability |
|-----------|-----------|
| OBSERVE | Commit history, contributor stats, branch topology, commit frequency |
| THINK | Impact analysis, symbol context, hotspot identification |
| VERIFY | Architecture impact detection via change mapping |

## Key Exports

- **`GitHistoryAnalyzer`** -- Git history analysis via GitPython (commit history, contributors, churn, topology)
- **`GitNexusBridge`** -- Structural code analysis via GitNexus knowledge graph (optional, requires Node.js)
- **`GITNEXUS_AVAILABLE`** -- Boolean flag indicating GitNexus availability

## MCP Tools

| Tool | Description |
|------|-------------|
| `git_analysis_index_repo` | Index a repository with GitNexus (Tree-sitter + KuzuDB) |
| `git_analysis_query` | Hybrid BM25 + semantic search over the knowledge graph |
| `git_analysis_symbol_context` | 360-degree dependency analysis for a symbol |
| `git_analysis_impact` | Blast-radius assessment for symbol changes |
| `git_analysis_detect_changes` | Map git diff to architectural impact |
| `git_analysis_cypher_query` | Raw Cypher query against KuzuDB graph |
| `git_analysis_list_indexed` | List all repositories in GitNexus registry |
| `git_analysis_commit_history` | Detailed commit history with per-commit stats |
| `git_analysis_contributor_stats` | Per-author aggregate statistics |
| `git_analysis_code_churn` | Top N most-frequently-changed files |
| `git_analysis_branch_topology` | Branch names, tips, and active branch |
| `git_analysis_commit_frequency` | Commit frequency by day/week/month |
| `git_analysis_filtered_history` | Filtered commits by date/author/branch |
| `git_analysis_file_history` | Commit history for a specific file |
| `git_analysis_directory_churn` | Churn aggregated by top-level directory |
| `git_analysis_hotspots` | Hotspot analysis combining churn with recency |

## Quick Start

```python
from codomyrmex.git_analysis import GitHistoryAnalyzer

analyzer = GitHistoryAnalyzer(".")
commits = analyzer.get_commit_history(max_count=10)
stats = analyzer.get_contributor_stats()
hotspots = analyzer.get_hotspot_analysis(top_n=5)
```

## Architecture

```
git_analysis/
  __init__.py             -- Package root; exports GitHistoryAnalyzer, GitNexusBridge
  mcp_tools.py            -- 16 MCP tool definitions (7 GitNexus + 9 GitPython)
  core/
    history_analyzer.py   -- GitHistoryAnalyzer (GitPython-based)
    gitnexus_bridge.py    -- GitNexusBridge (Node.js subprocess)
  vendor/
    gitnexus/             -- Vendored GitNexus source (skip in docs)
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/git_analysis/ -v
```

## Navigation

- [Root](../../../../../../README.md)
