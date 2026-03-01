# git_analysis API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module: `codomyrmex.git_analysis`

```python
from codomyrmex.git_analysis import GitHistoryAnalyzer, GitNexusBridge, GITNEXUS_AVAILABLE
```

---

## Class: `GitHistoryAnalyzer`

`codomyrmex.git_analysis.core.history_analyzer.GitHistoryAnalyzer`

Analyzes git history via GitPython (core dependency — always available).

### Constructor

```python
GitHistoryAnalyzer(repo_path: str) -> None
```

Initializes with the path to a git repository. Calls `git.Repo(path, search_parent_directories=True)`.

**Raises:** `git.InvalidGitRepositoryError` if path is not a git repo.

---

### `get_commit_history`

```python
def get_commit_history(
    self, max_count: int = 50, branch: str | None = None
) -> list[dict[str, Any]]
```

Returns commit metadata sorted newest-first.

**Parameters:**
- `max_count`: Maximum commits to return (default 50)
- `branch`: Branch to walk (default: active branch)

**Returns:** List of dicts, each containing:
```python
{
    "sha": str,          # 12-char short SHA
    "author": str,       # Author display name
    "email": str,        # Author email
    "date": str,         # ISO-8601 datetime with timezone
    "message": str,      # First line of commit message
    "insertions": int,   # Lines added
    "deletions": int,    # Lines removed
    "files_changed": int # Number of files touched
}
```

---

### `get_contributor_stats`

```python
def get_contributor_stats(self) -> list[dict[str, Any]]
```

Returns per-author aggregate statistics across ALL commits, sorted by commit count descending.

**Returns:** List of dicts:
```python
{
    "author": str,        # Author display name
    "commits": int,       # Total commit count
    "insertions": int,    # Total lines added
    "deletions": int,     # Total lines removed
    "first_commit": str,  # ISO-8601 date of earliest commit
    "last_commit": str    # ISO-8601 date of most recent commit
}
```

---

### `get_code_churn`

```python
def get_code_churn(self, top_n: int = 20) -> list[dict[str, Any]]
```

Returns the top N most-frequently-modified files.

**Parameters:**
- `top_n`: Number of files to return (default 20)

**Returns:** List of dicts, sorted by `change_count` descending:
```python
{
    "file": str,         # Relative file path
    "change_count": int  # Number of commits that touched this file
}
```

---

### `get_branch_topology`

```python
def get_branch_topology(self) -> dict[str, Any]
```

Returns branch names and their tip commits.

**Returns:**
```python
{
    "active_branch": str,  # Currently checked-out branch name
    "branch_count": int,   # Total number of local branches
    "branches": [          # One entry per local branch
        {
            "name": str,          # Branch name
            "tip_sha": str,       # 12-char short SHA of tip commit
            "tip_message": str,   # First line of tip commit message
            "tip_date": str       # ISO-8601 date of tip commit
        }
    ]
}
```

---

### `get_commit_frequency`

```python
def get_commit_frequency(self, by: str = "week") -> dict[str, int]
```

Returns commit counts bucketed by time period.

**Parameters:**
- `by`: Bucket size — `"day"` (YYYY-MM-DD), `"week"` (YYYY-WNN), or `"month"` (YYYY-MM)

**Returns:** Dict mapping period key → commit count, sorted chronologically.

---

### `get_commit_history_filtered`

```python
def get_commit_history_filtered(
    self,
    max_count: int = 50,
    since: str | None = None,
    until: str | None = None,
    author: str | None = None,
    branch: str | None = None,
) -> list[dict[str, Any]]
```

Returns commit history with optional date range and author filters.

**Parameters:**
- `max_count`: Maximum commits to return (default 50, capped at 10000)
- `since`: ISO-8601 date string — only commits after this date
- `until`: ISO-8601 date string — only commits before this date
- `author`: Author name substring filter (case-insensitive)
- `branch`: Branch to walk (default: active branch)

**Returns:** Same list shape as `get_commit_history()`.

---

### `get_file_history`

```python
def get_file_history(
    self,
    file_path: str,
    max_count: int = 50,
) -> list[dict[str, Any]]
```

Returns commit history for all commits that touched a specific file.

**Parameters:**
- `file_path`: Relative path to the file within the repository
- `max_count`: Maximum commits to return (default 50, capped at 10000)

**Returns:** Same list shape as `get_commit_history()`.

---

### `get_churn_by_directory`

```python
def get_churn_by_directory(self, top_n: int = 10) -> list[dict[str, Any]]
```

Returns commit frequency aggregated by top-level directory.

**Parameters:**
- `top_n`: Number of top directories to return (default 10)

**Returns:** List sorted by `change_count` descending:
```python
{
    "directory": str,   # Top-level directory name
    "change_count": int, # Number of commits that touched any file in this directory
    "files": int         # Number of distinct files touched
}
```

---

### `get_hotspot_analysis`

```python
def get_hotspot_analysis(self, top_n: int = 20) -> list[dict[str, Any]]
```

Identifies high-risk files by combining churn frequency with recency.
Score = `change_count / (1 + days_since_last_change / 30)`.

**Parameters:**
- `top_n`: Number of top hotspot files to return (default 20)

**Returns:** List sorted by `hotspot_score` descending:
```python
{
    "file": str,              # Relative file path
    "change_count": int,      # Number of commits that touched this file
    "last_changed": str,      # ISO-8601 datetime of most recent touch
    "hotspot_score": float    # Hotspot score (higher = more risky)
}
```

---

## Class: `GitNexusBridge`

`codomyrmex.git_analysis.core.gitnexus_bridge.GitNexusBridge`

Subprocess bridge to the GitNexus Node.js codebase-analysis tool.
Requires Node.js/npx or a built vendor distribution.

### Constructor

```python
GitNexusBridge(repo_path: str, vendor_dir: str | None = None) -> None
```

**Parameters:**
- `repo_path`: Path to the git repository to analyze
- `vendor_dir`: Override path to the vendor/gitnexus directory (optional)

---

### `check_availability`

```python
def check_availability(self) -> bool
```

Returns `True` if gitnexus is runnable. Safe to call without Node.js installed.

---

### `analyze`

```python
def analyze(self) -> dict[str, Any]
```

Index the repository (creates `.gitnexus/` knowledge graph). Run before other tools.

**Returns:** `{"stdout": str, "stderr": str, "indexed": True}`

**Note:** May take minutes for large repositories. Sets `timeout=300`.

---

### `query`

```python
def query(self, query_text: str, limit: int = 10) -> dict[str, Any]
```

Hybrid BM25 + semantic search over the knowledge graph.

---

### `get_context`

```python
def get_context(self, symbol: str) -> dict[str, Any]
```

360-degree dependency view for a symbol.

---

### `assess_impact`

```python
def assess_impact(self, symbol: str) -> dict[str, Any]
```

Blast-radius assessment — all symbols transitively affected by changing `symbol`.

---

### `detect_changes`

```python
def detect_changes(self, diff: str | None = None) -> dict[str, Any]
```

Map a git diff to architectural impact. Uses HEAD diff if `diff` is None.

---

### `run_cypher`

```python
def run_cypher(self, cypher_query: str) -> dict[str, Any]
```

Execute a raw Cypher query against the KuzuDB knowledge graph.

---

### `list_repos`

```python
def list_repos(self) -> list[dict[str, Any]]
```

List all repositories in the global `~/.gitnexus` registry.

---

## Exception: `GitNexusNotAvailableError`

```python
class GitNexusNotAvailableError(RuntimeError)
```

Raised by `_resolve_cmd()` when neither `npx` nor a built vendor dist is found.
Check `check_availability()` to guard against this before calling other methods.

---

## Module-level exports

```python
from codomyrmex.git_analysis import (
    GitHistoryAnalyzer,    # Always available
    GitNexusBridge,        # Available when GITNEXUS_AVAILABLE is True
    GitNexusNotAvailableError,  # Available when GITNEXUS_AVAILABLE is True
    GITNEXUS_AVAILABLE,    # bool — True if Node.js/npx is accessible
)
```
