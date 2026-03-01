# git_analysis Behavioral Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provides analytical intelligence about git repositories — not operational git commands
(that's `git_operations`). The split is:

- **git_analysis**: *What happened? Who did it? What depends on what?*
- **git_operations**: *Clone, commit, push, pull, branch management*

## Behavioral Constraints

### GitPython Analysis (always available)

1. **Direct git object access**: All history analysis uses GitPython's object model directly.
   No subprocess calls, no `git log` parsing. Fast and portable.

2. **No network access**: `GitHistoryAnalyzer` only reads the local git object database.
   Remote operations are out of scope.

3. **Sorted output**: `get_contributor_stats()` sorts by commit count descending.
   `get_commit_frequency()` sorts by time ascending (chronological).
   `get_code_churn()` sorts by change_count descending.

4. **search_parent_directories=True**: `git.Repo()` walks up from the given path to find
   the `.git/` directory. Works correctly when called from subdirectories.

5. **ISO-8601 dates with timezone**: All datetime outputs use `isoformat()` which
   preserves the commit's original timezone offset.

### GitNexus Bridge (requires Node.js/npx)

6. **Graceful degradation**: All 7 GitNexus MCP tools return `{"status": "error", ...}`
   rather than raising exceptions when Node.js is unavailable. They never crash.

7. **npx preference**: `_resolve_cmd()` prefers `npx --yes gitnexus` over vendor dist.
   This enables zero-install usage (npx downloads on first run).

8. **Vendor fallback**: If npx unavailable, tries `node vendor/gitnexus/dist/index.js`.
   Build the vendor dist with `cd vendor/gitnexus && npm install && npm run build`.

9. **Command caching**: `_resolve_cmd()` caches the resolved command list. Second call
   returns the same list object without re-checking PATH.

10. **analyze() is non-JSON**: GitNexus `analyze` emits status messages, not JSON.
    The bridge runs it without `--json` and returns `{"stdout": ..., "indexed": True}`.
    All other commands (query, context, impact, etc.) use `--json`.

11. **Timeout**: `analyze()` uses `timeout=300` (5 minutes). Other commands use `timeout=60`.

### MCP Tools

12. **Category**: All 16 tools declare `category="git_analysis"`.

13. **Error shape**: On exception, tools return `{"status": "error", "error": str(exc)}`.
    No exceptions propagate to callers.

14. **Lazy imports**: `_bridge()` and `_analyzer()` helpers avoid circular imports by
    deferring imports to first call. Pattern matches `git_operations/mcp_tools.py`.

15. **Fallback decorator**: If `codomyrmex.model_context_protocol.decorators.mcp_tool`
    is unavailable, a local stub decorator attaches `._mcp_tool_meta` to the function.
    This ensures auto-discovery works even when MCP is partially initialized.

## Submodule: vendor/gitnexus

The GitNexus Node.js tool is vendored as a git submodule:

```
.gitmodules entry:
[submodule "src/codomyrmex/git_analysis/vendor/gitnexus"]
    path = src/codomyrmex/git_analysis/vendor/gitnexus
    url = https://github.com/abhigyanpatwari/GitNexus
```

The submodule is initialized with `git submodule update --init` or
`git submodule add https://github.com/abhigyanpatwari/GitNexus src/codomyrmex/git_analysis/vendor/gitnexus`.

The vendor source is not built by default. Users who want vendor-mode operation
(without npx) must run `npm install && npm run build` in the vendor directory.

## Zero-Mock Policy Compliance

Tests in `tests/unit/git_analysis/` comply with the codomyrmex zero-mock policy:
- No `unittest.mock`, `MagicMock`, `monkeypatch`, or `pytest-mock`
- GitPython tests run against the actual codomyrmex git repository
- GitNexus integration tests use `@pytest.mark.skipif` guards for Node.js availability
- Error path tests use invalid paths (not mocked exceptions)

## Dependency: GitPython

`git` (GitPython >=3.1.0) is declared in `pyproject.toml` under `[project.dependencies]`.
It is a core dependency — available in all codomyrmex installations without extra flags.

## Dependency: Node.js / GitNexus

GitNexus is a Node.js tool. It is NOT a Python package and NOT in `pyproject.toml`.
Installation options:
1. `npm install -g gitnexus` — global install
2. `npx gitnexus` — automatic download on first use (zero-install)
3. Vendor build — `npm install && npm run build` in `vendor/gitnexus/`
