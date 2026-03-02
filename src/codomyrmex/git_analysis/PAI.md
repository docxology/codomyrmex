# git_analysis — PAI Integration

Maps the git_analysis module capabilities to PAI Algorithm phases.

## Phase → Tool Mapping

| Phase | Recommended Tools | Use Case |
|-------|------------------|----------|
| **OBSERVE** | `git_analysis_contributor_stats`, `git_analysis_commit_history`, `git_analysis_query` | Understand who built what, recent changes, code structure context |
| **THINK** | `git_analysis_code_churn`, `git_analysis_symbol_context` | Identify risky files, understand symbol dependencies |
| **PLAN** | `git_analysis_branch_topology`, `git_analysis_impact` | Understand branch state, assess blast radius of planned changes |
| **BUILD** | `git_analysis_detect_changes` | Map in-progress changes to architectural impact |
| **EXECUTE** | — | No direct use during execution |
| **VERIFY** | `git_analysis_commit_frequency`, `git_analysis_contributor_stats` | Confirm commits landed, track development velocity |
| **LEARN** | `git_analysis_code_churn`, `git_analysis_query` | Identify patterns for future ISC creation |

## OBSERVE Phase Usage

When starting a session on the codomyrmex codebase:

```python
from codomyrmex.git_analysis.mcp_tools import (
    git_analysis_contributor_stats,
    git_analysis_commit_history,
    git_analysis_code_churn,
)

# Understand recent changes
history = git_analysis_commit_history(repo_path=".", max_count=10)
# → shows what changed in the last 10 commits

# High-churn files = risky areas requiring more ISC criteria
churn = git_analysis_code_churn(repo_path=".", top_n=20)
# → pyproject.toml (42x), src/codomyrmex/__init__.py (37x) — volatile files

# Understanding ownership
stats = git_analysis_contributor_stats(repo_path=".")
# → Daniel Ari Friedman: 124 commits | NewTester: 110 commits
```

## PLAN Phase Usage

Before making changes, assess impact:

```python
from codomyrmex.git_analysis.mcp_tools import (
    git_analysis_branch_topology,
    git_analysis_impact,  # requires gitnexus index
)

# Verify branch state
topology = git_analysis_branch_topology(repo_path=".")
# → active_branch: "main", 2 branches

# Blast radius (if GitNexus indexed)
impact = git_analysis_impact(repo_path=".", symbol="GitHistoryAnalyzer")
# → shows all tools/callers affected by changes to this class
```

## Generating ISC from git_analysis

High-churn files identified by `get_code_churn()` should generate additional ISC anti-criteria:

```
ISC-A-N: "High-churn files X, Y, Z are not modified without tests"
ISC-A-N: "No regressions introduced to modules with >30 churn touches"
```

Contributor patterns inform agent delegation:
- High commit-count areas → more detailed ISC for those modules
- Recent large insertions → areas needing verification focus

## Agent Types That Use This Module

| Agent Type | Usage |
|-----------|-------|
| **Engineer** | `git_analysis_commit_history` to understand recent context before edits |
| **Architect** | `git_analysis_impact` + `git_analysis_symbol_context` for system design |
| **QATester** | `git_analysis_code_churn` to prioritize high-risk test coverage |
| **Algorithm** | `git_analysis_contributor_stats` + `git_analysis_commit_frequency` for ISC |

## MCP Tools

| Tool | Description | Key Parameters | PAI Phase |
|------|-------------|----------------|-----------|
| `git_analysis__analyze_repo` | Full repository analysis | `repo_path: str` | OBSERVE |
| `git_analysis__get_commit_history` | Retrieve commit log with filters | `repo_path, limit, author` | OBSERVE |
| `git_analysis__get_contributor_stats` | Contributor activity and commit stats | `repo_path: str` | OBSERVE |
| `git_analysis__get_file_history` | History of changes to a specific file | `repo_path, file_path` | OBSERVE |
| `git_analysis__detect_patterns` | Detect commit patterns and trends | `repo_path: str` | OBSERVE |
| `git_analysis__get_branch_info` | Branch metadata and divergence info | `repo_path: str` | OBSERVE |
| `git_analysis__get_blame` | Line-by-line blame attribution | `repo_path, file_path` | OBSERVE |
| `git_analysis__get_tags` | Repository tags and versions | `repo_path: str` | OBSERVE |
| `git_analysis__get_diff` | Diff between commits or branches | `repo_path, from_ref, to_ref` | OBSERVE |
| `git_analysis__get_hotspots` | Files with most churn/changes | `repo_path: str` | OBSERVE |
| `git_analysis__get_code_age` | Age of code by file/function | `repo_path: str` | OBSERVE |
| `git_analysis__get_first_commit` | First commit metadata | `repo_path: str` | OBSERVE |
| `git_analysis__get_commit_frequency` | Commit frequency over time | `repo_path, interval` | OBSERVE |
| `git_analysis__get_coauthors` | Co-author collaboration patterns | `repo_path: str` | OBSERVE |
| `git_analysis__get_merge_patterns` | Merge strategy and frequency | `repo_path: str` | OBSERVE |
| `git_analysis__summarize_repo` | High-level repository summary | `repo_path: str` | OBSERVE |

## MCP Bridge Discovery

This module is auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
scan in `mcp_tools.py`. No manual registration needed. The bridge surfaces all 16
tools when `pkgutil` scans `codomyrmex.git_analysis.mcp_tools`.
