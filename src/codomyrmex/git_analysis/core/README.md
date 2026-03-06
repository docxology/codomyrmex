# Git Analysis Core

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

The core sub-package provides the two primary analysis engines for the git_analysis module: `GitHistoryAnalyzer` for git commit history and contributor analytics (using GitPython), and `GitNexusBridge` for structural code analysis via the GitNexus Node.js knowledge graph tool (using subprocess). These components complement each other -- history analysis operates on git commit metadata while structural analysis operates on AST-level symbol dependencies.

## Architecture

```
core/
  __init__.py              # Exports GitHistoryAnalyzer, GitNexusBridge, GitNexusNotAvailableError
  history_analyzer.py      # GitPython-based commit history and contributor analysis
  gitnexus_bridge.py       # Subprocess bridge to GitNexus CLI (Node.js)
```

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `GitHistoryAnalyzer` | Class | Commit history, contributor stats, code churn, branch topology, hotspot analysis |
| `GitNexusBridge` | Class | Subprocess bridge to GitNexus for structural code queries, impact analysis, and Cypher queries |
| `GitNexusNotAvailableError` | Exception | Raised when neither npx nor vendored GitNexus build is found |

## GitHistoryAnalyzer

Analyzes git history using GitPython's object model directly (no subprocess calls). All methods operate on the git object model, making them fast and portable. Requires GitPython (core dependency, no extra install).

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_commit_history(max_count, branch)` | Commit metadata list (sha, author, date, message, insertions, deletions, files_changed) sorted newest-first | `list[dict]` |
| `get_contributor_stats()` | Per-author aggregates across all commits (commit count, insertions, deletions, first/last commit) sorted by commit count | `list[dict]` |
| `get_code_churn(top_n)` | Top N most-frequently-changed files (churn = number of commits touching the file) | `list[dict]` |
| `get_branch_topology()` | Branch names, tip commits, active branch | `dict` |
| `get_commit_frequency(by)` | Commit counts bucketed by time period ("day", "week", or "month") | `dict[str, int]` |
| `get_commit_history_filtered(max_count, since, until, author, branch)` | Filtered commit history with optional date range and author substring filter | `list[dict]` |
| `get_file_history(file_path, max_count)` | Commit history for a specific file path | `list[dict]` |
| `get_churn_by_directory(top_n)` | Commit frequency aggregated by top-level directory | `list[dict]` |
| `get_hotspot_analysis(top_n)` | High-risk files combining churn frequency with recency. Score = change_count / (1 + days_since_last_change/30) | `list[dict]` |

### Usage

```python
from codomyrmex.git_analysis.core import GitHistoryAnalyzer

analyzer = GitHistoryAnalyzer(".")

# Recent commits
commits = analyzer.get_commit_history(max_count=10)
for c in commits:
    print(f"{c['sha']} {c['author']}: {c['message']}")

# Contributor leaderboard
stats = analyzer.get_contributor_stats()
for s in stats[:5]:
    print(f"{s['author']}: {s['commits']} commits, +{s['insertions']}/-{s['deletions']}")

# Code churn hotspots
churn = analyzer.get_code_churn(top_n=10)
for f in churn:
    print(f"{f['file']}: {f['change_count']} changes")

# Hotspot analysis (churn weighted by recency)
hotspots = analyzer.get_hotspot_analysis(top_n=10)
for h in hotspots:
    print(f"{h['file']}: score={h['hotspot_score']}, changes={h['change_count']}")

# Branch topology
topology = analyzer.get_branch_topology()
print(f"Active: {topology['active_branch']}, Branches: {topology['branch_count']}")

# Filtered history
recent = analyzer.get_commit_history_filtered(
    max_count=20, since="2026-01-01", author="daniel"
)
```

## GitNexusBridge

Subprocess bridge to the GitNexus Node.js CLI tool. GitNexus indexes a repository using Tree-sitter AST parsing and KuzuDB graph storage, then exposes structural query tools. It analyzes code structure (symbol dependencies, call chains, blast radius) rather than git commit history.

### Prerequisites

Requires one of:
- `npx` on PATH (preferred, zero-install)
- Built vendor distribution at `vendor/gitnexus/dist/index.js` with `node` on PATH

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `check_availability()` | Check if GitNexus is runnable | `bool` |
| `analyze()` | Index the repository (creates `.gitnexus/` directory). Must run before queries. May take minutes for large repos. | `dict` |
| `query(query_text, limit)` | Hybrid BM25 + semantic search over the knowledge graph | `dict` |
| `get_context(symbol)` | 360-degree analysis: incoming + outgoing dependencies for a symbol | `dict` |
| `assess_impact(symbol)` | Blast-radius assessment with confidence scoring | `dict` |
| `detect_changes(diff)` | Map a git diff to architectural impact | `dict` |
| `run_cypher(cypher_query)` | Execute raw Cypher query against KuzuDB graph | `dict` |
| `list_repos()` | List all repos indexed in the global `~/.gitnexus` registry | `list[dict]` |

### Usage

```python
from codomyrmex.git_analysis.core import GitNexusBridge, GitNexusNotAvailableError

bridge = GitNexusBridge(".")

if bridge.check_availability():
    # Index the repository first
    bridge.analyze()

    # Search for symbols
    results = bridge.query("FileSystemManager", limit=5)

    # Get symbol context (incoming + outgoing deps)
    context = bridge.get_context("FileSystemManager.read_file")

    # Assess blast radius of a change
    impact = bridge.assess_impact("FileSystemManager.delete")

    # Raw Cypher query
    graph_data = bridge.run_cypher("MATCH (n:Symbol) RETURN n.name LIMIT 10")
else:
    print("GitNexus not available (install Node.js or build vendor)")
```

## Error Handling

- `GitHistoryAnalyzer.__init__()` raises `git.InvalidGitRepositoryError` if the path is not a git repository.
- `GitNexusBridge` raises `GitNexusNotAvailableError` when neither npx nor vendored build is found.
- `GitNexusBridge._run()` raises `RuntimeError` on non-zero exit codes from the GitNexus CLI.
- `GitNexusBridge._run()` respects a configurable timeout (default 60s, 300s for `analyze()`).

## Testing

```bash
# History analyzer tests (requires a git repository)
uv run pytest src/codomyrmex/tests/unit/git_analysis/ -v

# GitNexus bridge tests (requires Node.js/npx)
uv run pytest src/codomyrmex/tests/unit/git_analysis/ -v -k "gitnexus"
```

Tests use `@pytest.mark.skipif` guards when Git or Node.js dependencies are unavailable.

## Navigation

- [AGENTS](AGENTS.md) | [SPEC](SPEC.md) | [Parent](../README.md)
