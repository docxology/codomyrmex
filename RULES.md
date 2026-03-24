# Codomyrmex Operating Rules

This document codifies the absolute, non-negotiable rules for all human and AI agent contributors operating within the Codomyrmex repository. These tenets prioritize maximum intelligence, structural integrity, and verified functionality.

## 1. Zero-Mock Policy (Iron Law)
- **Never use mocks.** All tests and verifications must use real, functional components and authentic data paths.
- We exclusively build and rely upon real, tested, and documented functional methods.
- "Fake" or "Mock" structures are strictly forbidden. Use concrete `InMemory` or `Test` implementations only if external network boundaries are impossible to cross, and even then, test the data contracts holistically.

## 2. Modularity & Functionality
- Operations must be modular and functional. Changes within one module should strictly minimize blast radius impact on others.
- **Impact Analysis (GitNexus)**: Before modifying any function, class, or method, you MUST run a GitNexus impact analysis (`gitnexus_impact`) to assess direct callers, affected processes, and risk level. If risk is HIGH or CRITICAL, warn the user before proceeding.
- Always run `gitnexus_detect_changes()` before committing to verify modifications only affect expected execution flows.

## 3. Pythonic Ecosystem & Tooling
- Adhere strictly to modern Pythonic style.
- Use `uv` comprehensively for all Python environment management, dependency resolution, and script setup.
- Avoid legacy patterns (e.g., standard `pip` or `Poetry`); leverage `uv run`, `pyproject.toml`, and `uv.lock`.

## 4. Documentation Triangulation
- You must triple-check all filenames, paths, and signposting.
- Documentation must be perfectly mirrored and synchronized. When making structural changes, you must synchronously update:
  - `AGENTS.md` (Agent coordination)
  - `README.md` (Human entry point)
  - `SPEC.md` (Functional specification)
  - This applies at all folder levels.
- Always verify that all methods are fully documented, clear, and streamlined.

## 5. Comprehensive Verification
- Execute iteratively, comprehensively, and intelligently step-by-step.
- Every introduced feature must be backed by the modular, unified, streamlined test suite anywhere it is added completely.
- Maintain the repository coverage gate: **40%** minimum line coverage per `pyproject.toml` (see `[tool.coverage.report]` and pytest `addopts`). No production code can be introduced without a corresponding failing-then-passing test (TDD methodology).

## 6. MCP Universal Protocols
- Preserve all Model Context Protocol (MCP) interfaces. Tool specifications must remain available and perfectly functional for sibling agents.
- When generating `@mcp_tool` functions, ensure standard input/output payload structures (typically returning status dicts like `{"status": "success", ...}`).

Following these rules ensures the Codomyrmex ecosystem remains supercritical, strictly reliable, and flawlessly modular.
