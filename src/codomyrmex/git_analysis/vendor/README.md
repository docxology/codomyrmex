# git_analysis/vendor — Vendored Dependencies

This directory contains third-party tools vendored directly into codomyrmex
rather than installed as pip packages.

## Contents

| Directory | Tool | Version | Source |
|-----------|------|---------|--------|
| `gitnexus/` | GitNexus | git submodule | [abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus) |

## GitNexus

**GitNexus** is a Node.js tool that builds a KuzuDB knowledge graph over a codebase
using Tree-sitter AST parsing. It enables structural code analysis queries — call
graphs, blast radius, semantic search.

It is vendored as a **git submodule** rather than an npm dependency because:
- The codomyrmex `git_analysis` module wraps it via subprocess (`npx gitnexus`)
- Vendoring ensures availability even without network access
- The submodule tracks a specific commit for reproducibility

### Using GitNexus via codomyrmex

Agents and users should NOT invoke GitNexus directly. Use MCP tools:

```python
from codomyrmex.git_analysis import GITNEXUS_AVAILABLE
# True if node/npx is available on PATH

# Via MCP:
# git_analysis_index_repo(repo_path=".")
# git_analysis_query(repo_path=".", query_text="authentication flow")
# git_analysis_impact(repo_path=".", symbol="MyClass")
```

### Building the vendor dist (optional)

```bash
cd src/codomyrmex/git_analysis/vendor/gitnexus
npm install
npm run build
# dist/index.js is now available as fallback when npx is unavailable
```

## Updating Vendored Dependencies

### GitNexus submodule

```bash
# Update to latest commit
git submodule update --remote src/codomyrmex/git_analysis/vendor/gitnexus

# Pin to specific commit
cd src/codomyrmex/git_analysis/vendor/gitnexus
git checkout <commit-sha>
cd ../../../..
git add src/codomyrmex/git_analysis/vendor/gitnexus
git commit -m "chore(git_analysis): pin gitnexus submodule to <sha>"
```

## Related

- `../core/gitnexus_bridge.py` — Python bridge that calls GitNexus via subprocess
- `../mcp_tools.py` — MCP tool wrappers for GitNexus operations
- `.gitmodules` (project root) — Submodule registry
