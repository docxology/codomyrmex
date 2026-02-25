# git_analysis/vendor — Agent Context

## CRITICAL: Do Not Modify Contents

The `gitnexus/` subdirectory is a **git submodule** pointing to an external
third-party repository. Do NOT create, edit, or delete files inside `gitnexus/`.

## Purpose

This `vendor/` directory holds third-party tools needed by `git_analysis` that
are vendored (included directly) rather than installed as package dependencies.

## Current Contents

| Directory | Type | What It Is |
|-----------|------|-----------|
| `gitnexus/` | git submodule | GitNexus — knowledge graph tool for structural code analysis |

## When Agents Should Access This Directory

**Read `vendor/README.md`** when you need to:
- Understand why GitNexus is vendored
- Find instructions for building the vendor dist
- Understand how to update the submodule

**Do NOT touch `gitnexus/` internals** — it is an external submodule.
Any RASP docs missing inside `gitnexus/` are intentional (we don't own that code).

## Quick Checks

```bash
# Is the submodule checked out?
ls src/codomyrmex/git_analysis/vendor/gitnexus/

# Is it initialized?
git submodule status src/codomyrmex/git_analysis/vendor/gitnexus

# What commit is it pinned to?
cd src/codomyrmex/git_analysis/vendor/gitnexus && git log --oneline -1
```

## GitNexus Availability

The `git_analysis` module gracefully handles GitNexus being unavailable:
```python
from codomyrmex.git_analysis import GITNEXUS_AVAILABLE
# True if node/npx is on PATH; False otherwise
# All GitNexus MCP tools return {"status": "error"} when unavailable
```

## Related

- `../core/gitnexus_bridge.py` — Python interface to the vendored GitNexus tool
- `../README.md` — Full git_analysis module documentation
