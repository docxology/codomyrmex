# git_analysis MCP Tool Specification

16 tools in category `git_analysis`. All return `{"status": "ok", ...}` on success
or `{"status": "error", "error": "<message>"}` on failure.

---

## GitNexus Tools (structural code analysis — requires Node.js/npx)

### `git_analysis_index_repo`

Index a repository with GitNexus. Creates `.gitnexus/` knowledge graph.
**Must be called before** query/context/impact tools.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `repo_path` | `str` | Yes | Absolute or relative path to the git repository |

**Returns on success:**
```json
{
  "status": "ok",
  "repo_path": "/path/to/repo",
  "result": {"stdout": "...", "stderr": "...", "indexed": true}
}
```

---

### `git_analysis_query`

Hybrid BM25 + semantic search over the GitNexus knowledge graph.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `repo_path` | `str` | Yes | — | Path to the indexed repository |
| `query_text` | `str` | Yes | — | Natural language or symbol name to search |
| `limit` | `int` | No | 10 | Maximum number of results |

**Returns on success:**
```json
{
  "status": "ok",
  "query": "authentication module",
  "results": { ... }
}
```

---

### `git_analysis_symbol_context`

360-degree symbol analysis: all incoming and outgoing dependencies.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `repo_path` | `str` | Yes | Path to the indexed repository |
| `symbol` | `str` | Yes | Fully-qualified symbol (e.g., `"MyClass.my_method"`) |

**Returns on success:**
```json
{
  "status": "ok",
  "symbol": "GitHistoryAnalyzer",
  "context": { "incoming": [...], "outgoing": [...] }
}
```

---

### `git_analysis_impact`

Blast-radius assessment: all symbols transitively affected by changing `symbol`.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `repo_path` | `str` | Yes | Path to the indexed repository |
| `symbol` | `str` | Yes | Symbol to assess blast radius for |

**Returns on success:**
```json
{
  "status": "ok",
  "symbol": "GitHistoryAnalyzer",
  "impact": { "affected": [...], "confidence": 0.87 }
}
```

---

### `git_analysis_detect_changes`

Map a git diff to architectural impact using the knowledge graph.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `repo_path` | `str` | Yes | — | Path to the indexed repository |
| `diff` | `str` | No | `null` | Unified diff string. Uses HEAD diff if null |

**Returns on success:**
```json
{
  "status": "ok",
  "impact": { "modules_affected": [...], "symbols_changed": [...] }
}
```

---

### `git_analysis_cypher_query`

Execute a raw Cypher query against the KuzuDB knowledge graph.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `repo_path` | `str` | Yes | Path to the indexed repository |
| `cypher_query` | `str` | Yes | Cypher query string (KuzuDB dialect) |

**Returns on success:**
```json
{
  "status": "ok",
  "query": "MATCH (n:Function) RETURN n.name LIMIT 10",
  "result": { "rows": [...] }
}
```

---

### `git_analysis_list_indexed`

List all repositories in the global `~/.gitnexus` registry.

**Parameters:** None

**Returns on success:**
```json
{
  "status": "ok",
  "repos": [{"name": "codomyrmex", "path": "/path/to/repo"}],
  "count": 1
}
```

---

## GitPython Tools (git history analysis — always available)

### `git_analysis_commit_history`

Detailed commit history with per-commit statistics.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `repo_path` | `str` | No | `"."` | Path to the git repository |
| `max_count` | `int` | No | 50 | Maximum commits to return |
| `branch` | `str \| null` | No | `null` | Branch to walk (default: active branch) |

**Returns on success:**
```json
{
  "status": "ok",
  "count": 50,
  "commits": [
    {
      "sha": "b81e9dabeae1",
      "author": "Daniel Ari Friedman",
      "email": "daniel@example.com",
      "date": "2026-02-24T07:16:25-08:00",
      "message": "fix: replace flaky PDF test with SVG",
      "insertions": 42,
      "deletions": 18,
      "files_changed": 5
    }
  ]
}
```

---

### `git_analysis_contributor_stats`

Per-author aggregate statistics across all commits.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `repo_path` | `str` | No | `"."` | Path to the git repository |

**Returns on success:**
```json
{
  "status": "ok",
  "count": 4,
  "contributors": [
    {
      "author": "Daniel Ari Friedman",
      "commits": 124,
      "insertions": 4704311,
      "deletions": 4013172,
      "first_commit": "2025-05-16T09:36:36-07:00",
      "last_commit": "2026-02-12T16:37:30-08:00"
    }
  ]
}
```

---

### `git_analysis_code_churn`

Top N most-frequently-changed files.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `repo_path` | `str` | No | `"."` | Path to the git repository |
| `top_n` | `int` | No | 20 | Number of top-churned files |

**Returns on success:**
```json
{
  "status": "ok",
  "count": 20,
  "files": [
    {"file": "README.md", "change_count": 58},
    {"file": "TO-DO.md", "change_count": 46}
  ]
}
```

---

### `git_analysis_branch_topology`

Branch names, tip commits, and active branch.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `repo_path` | `str` | No | `"."` | Path to the git repository |

**Returns on success:**
```json
{
  "status": "ok",
  "active_branch": "main",
  "branch_count": 2,
  "branches": [
    {
      "name": "main",
      "tip_sha": "b81e9dabeae1",
      "tip_message": "fix: replace flaky PDF test with SVG",
      "tip_date": "2026-02-24T07:16:25-08:00"
    }
  ]
}
```

---

### `git_analysis_commit_frequency`

Commit counts bucketed by time period.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `repo_path` | `str` | No | `"."` | Path to the git repository |
| `by` | `str` | No | `"week"` | Bucket: `"day"` (YYYY-MM-DD), `"week"` (YYYY-WNN), `"month"` (YYYY-MM) |

**Returns on success:**
```json
{
  "status": "ok",
  "bucket": "month",
  "frequency": {
    "2025-05": 6,
    "2026-02": 144
  }
}
```

---

### `git_analysis_filtered_history`

Filtered commit history with optional date range, author, and branch constraints.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `repo_path` | `str` | No | `"."` | Path to the git repository |
| `max_count` | `int` | No | 50 | Maximum commits to return |
| `since` | `str \| null` | No | `null` | ISO-8601 date — only commits after this date |
| `until` | `str \| null` | No | `null` | ISO-8601 date — only commits before this date |
| `author` | `str \| null` | No | `null` | Author name substring filter (case-insensitive) |
| `branch` | `str \| null` | No | `null` | Branch to walk (default: active branch) |

**Returns on success:** Same shape as `git_analysis_commit_history`.
```json
{
  "status": "ok",
  "count": 12,
  "commits": [{ "sha": "...", "author": "...", "date": "...", "message": "..." }]
}
```

---

### `git_analysis_file_history`

All commits that touched a specific file path.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `repo_path` | `str` | No | `"."` | Path to the git repository |
| `file_path` | `str` | Yes | — | Relative path to the file within the repository |
| `max_count` | `int` | No | 50 | Maximum commits to return |

**Returns on success:**
```json
{
  "status": "ok",
  "file": "src/codomyrmex/git_analysis/mcp_tools.py",
  "count": 8,
  "commits": [{ "sha": "...", "author": "...", "date": "...", "message": "..." }]
}
```

---

### `git_analysis_directory_churn`

Commit frequency aggregated by top-level directory. Identifies which modules have the most git activity.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `repo_path` | `str` | No | `"."` | Path to the git repository |
| `top_n` | `int` | No | 10 | Number of top directories to return |

**Returns on success:**
```json
{
  "status": "ok",
  "count": 10,
  "directories": [
    {"directory": "src", "change_count": 312, "files": 87}
  ]
}
```

---

### `git_analysis_hotspots`

Hotspot analysis combining churn frequency with recency. Score = `change_count / (1 + days_since_last_change / 30)`. High-score files are both frequently changed and recently touched.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `repo_path` | `str` | No | `"."` | Path to the git repository |
| `top_n` | `int` | No | 20 | Number of top hotspot files to return |

**Returns on success:**
```json
{
  "status": "ok",
  "count": 20,
  "hotspots": [
    {
      "file": "README.md",
      "change_count": 58,
      "last_changed": "2026-02-24T07:16:25",
      "hotspot_score": 55.2
    }
  ]
}
```
