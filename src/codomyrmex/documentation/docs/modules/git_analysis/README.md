<!-- readme: generated -->

# git_analysis

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/git_analysis/`

## Overview

Git analysis module for Codomyrmex.

Provides two complementary capabilities:

  - **GitNexus bridge**: structural code analysis via knowledge graph
    (requires Node.js/npx; vendored at vendor/gitnexus/)
    → symbol dependencies, call chains, blast-radius assessment

  - **Git history analysis**: commit history, contributors, code churn,
    branch topology (via GitPython — a core dependency)
    → commit frequency, contributor stats, high-churn file detection

Both capabilities are exposed as MCP tools in mcp_tools.py (16 total).

## Public Exports

`git_analysis` exports 2 public symbols via `__all__`:

`GITNEXUS_AVAILABLE`, `GitHistoryAnalyzer`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../git_analysis/](../../../../git_analysis/)
