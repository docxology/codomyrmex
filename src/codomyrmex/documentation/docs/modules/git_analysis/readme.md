# git_analysis

Repository analysis module for Codomyrmex. Provides two complementary capabilities for understanding codebases:

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Analyze git history to understand codebase evolution and contribution patterns | 16 `git_analysis_*` tools |
| **THINK** | Identify code hotspots and contributor expertise for capability selection | `git_analysis_*` analysis tools |
| **LEARN** | Archive commit patterns for future baseline comparisons | `git_analysis_*` pattern tools |

PAI's OBSERVE phase uses git analysis to understand the codebase: commit timeline, contributor stats, and pattern detection inform THINK phase capability selection. 16 MCP tools cover commit analysis, author statistics, file evolution, and pattern detection.

## Capabilities

### 1. GitPython History Analysis (always available)

Analytical capabilities built on **GitPython** (a core codomyrmex dependency):

| Tool | Description |
|------|-------------|
| `get_commit_history()` | Commit metadata with per-commit stats (insertions/deletions/files) |
| `get_contributor_stats()` | Aggregate per-author stats across all commits |
| `get_code_churn()` | Top N most-frequently-changed files |
| `get_branch_topology()` | Branch names, tip commits, and active branch |
| `get_commit_frequency()` | Commit counts bucketed by day, week, or month |
| `get_commit_history_filtered()` | Filtered history by date range, author, or branch |
| `get_file_history()` | Commit history for a specific file path |
| `get_churn_by_directory()` | Commit frequency aggregated by top-level directory |
| `get_hotspot_analysis()` | Hotspot score combining churn frequency and recency |

### 2. GitNexus Structural Analysis (requires Node.js/npx)

Structural code analysis via [GitNexus](https://github.com/abhigyanpatwari/GitNexus) — a Tree-sitter AST parsing + KuzuDB knowledge graph tool vendored at `vendor/gitnexus/`:

| Tool | Description |
|------|-------------|
| `analyze()` | Index a repository (creates `.gitnexus/` knowledge graph) |
| `query()` | Hybrid BM25 + semantic search over the graph |
| `get_context()` | 360-degree symbol dependency view |
| `assess_impact()` | Blast-radius assessment for symbol changes |
| `detect_changes()` | Map a git diff to architectural impact |
| `run_cypher()` | Raw Cypher queries against the KuzuDB graph |
| `list_repos()` | List all repos in the global GitNexus registry |

## Quick Start

```python
from codomyrmex.git_analysis import GitHistoryAnalyzer, GITNEXUS_AVAILABLE

# Git history analysis (always available)
analyzer = GitHistoryAnalyzer(".")
stats = analyzer.get_contributor_stats()
print(f"Top contributor: {stats[0]['author']} ({stats[0]['commits']} commits)")

churn = analyzer.get_code_churn(top_n=10)
print("Most-changed files:")
for f in churn:
    print(f"  {f['change_count']}x {f['file']}")

# GitNexus (requires Node.js/npx)
if GITNEXUS_AVAILABLE:
    from codomyrmex.git_analysis import GitNexusBridge
    bridge = GitNexusBridge(".")
    bridge.analyze()  # Index the repo
    results = bridge.query("authentication module")
```

## MCP Tools

All capabilities are exposed as 16 MCP tools (see `MCP_TOOL_SPECIFICATION.md`):
- 7 GitNexus tools: `git_analysis_index_repo`, `git_analysis_query`, etc.
- 9 GitPython tools: `git_analysis_commit_history`, `git_analysis_contributor_stats`,
  `git_analysis_filtered_history`, `git_analysis_file_history`,
  `git_analysis_directory_churn`, `git_analysis_hotspots`, etc.

## Architecture

```
git_analysis/
├── __init__.py              # GitHistoryAnalyzer + conditional GitNexusBridge
├── mcp_tools.py             # 16 MCP tools
├── core/
│   ├── history_analyzer.py  # GitPython-based analysis
│   └── gitnexus_bridge.py   # Node.js subprocess bridge
├── vendor/
│   └── gitnexus/            # Git submodule (abhigyanpatwari/GitNexus)
└── data/
    └── codomyrmex_description.md  # Live analysis of this repo
```

## Distinction from git_operations

- **git_operations**: *Operational* — clone, commit, push, pull, branch management
- **git_analysis**: *Analytical* — "what happened?", "who did what?", "what depends on what?"

Both modules can be used together: use `git_operations` to manage repos, then `git_analysis` to understand their history and structure.

## Requirements

- **GitPython history tools**: No extra dependencies (GitPython is a core dep)
- **GitNexus structural tools**: Node.js + npm/npx (or built vendor dist)
  - Install: `npm install -g gitnexus` or use `npx` (zero-install)
  - Vendor build: `cd vendor/gitnexus && npm install && npm run build`

## Navigation

- **Extended Docs**: [docs/modules/git_analysis/](../../../docs/modules/git_analysis/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README.md](../../../README.md)
