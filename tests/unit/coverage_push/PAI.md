# Personal AI Infrastructure — Coverage Push

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Coverage Push is a targeted test area that validates the eight highest-gap Tier-1/2
modules of Codomyrmex, raising line coverage toward the **60%** release floor
(`[tool.coverage.report] fail_under` in `pyproject.toml`). It provides validation
coverage, fixtures, and regression checks so that AI agents and CI can rely on these
modules without mocking.

Per the project's **Zero-Mock Policy**, every test in this area exercises real
components through their public APIs — no mocks, no stubs. Narrow
`monkeypatch.setenv`/`chdir` and `tmp_path` fixtures are used only for test-input
isolation (see [docs/development/testing-strategy.md](../../../docs/development/testing-strategy.md)).

## Coverage Surface

| Tier | Module | Test File | What Is Exercised |
| :--- | :--- | :--- | :--- |
| 1 | `cerebrum/` | `test_tier1_modules.py` | `Model`/`ReasoningResult` dataclasses, `CerebrumConfig`, `AdaptationTransformer`/`LearningTransformer`, `TransformationManager` |
| 1 | `fpf/` | `test_tier1_modules.py` | `Pattern`/`Concept`/`Relationship` models, `FPFSpec`, `FPFIndex` search |
| 1 | `containerization/` | `test_tier1_modules.py` | `ContainerConfig` defaults/name resolution, `DockerManager` import + recommendation path (Docker need not be present) |
| 1 | `git_operations/` | `test_tier1_modules.py` | Package import surface, `mcp_tools` exports (`git_repo_status`) |
| 2 | `data_visualization/` | `test_tier2_modules.py` | `BaseComponent`, `Badge`, `Alert` renderers; `LinePlot` + `create_line_plot` (empty-data rejection, marker/multi-line paths) |
| 2 | `documentation/` | `test_tier2_modules.py` | `DocumentationQualityAnalyzer` completeness/consistency/structure scoring, `generate_quality_report` |
| 2 | `coding/` | `test_tier2_modules.py` | `validate_timeout` clamping, `SUPPORTED_LANGUAGES`, `execute_code` input validation (no sandbox required) |
| 2 | `agents/` | `test_tier2_modules.py` | `ProbeResult`, `AgentDescriptor`, `AgentRegistry` listing/probing (live-probe tolerant) |

## PAI Capabilities

### Regression Guardrails for AI-Editing Workflows

When an agent edits one of the covered modules, these tests are the first-line
regression check:

```python
import subprocess

result = subprocess.run(
    ["uv", "run", "pytest", "tests/unit/coverage_push/"], check=False
)
print(f"Exit status: {result.returncode}")
```

### Coverage-Gap Discovery

Before extending coverage, confirm which module areas remain uncovered:

```python
import subprocess

result = subprocess.run(
    [
        "uv", "run", "pytest",
        "--cov=codomyrmex.cerebrum",
        "--cov=codomyrmex.fpf",
        "--cov=codomyrmex.containerization",
        "--cov=codomyrmex.git_operations",
        "--cov=codomyrmex.data_visualization",
        "--cov=codomyrmex.documentation",
        "--cov=codomyrmex.coding",
        "--cov=codomyrmex.agents",
        "--cov-report=term-missing",
        "tests/unit/coverage_push/",
    ],
    check=False,
)
```

### Extending Coverage (AI Strategy)

When adding new tests here, follow the established pattern:

1. **Target the public API**: import from the module's public surface (e.g.
   `codomyrmex.cerebrum.core.models`), never private internals.
2. **Stay real**: drive actual dataclasses/config objects and real function calls;
   do not mock the component under test.
3. **Keep it fast and environment-independent**: like `ContainerConfig` and
   `execute_code` validation, prefer paths that do not require Docker, a live git
   repo, or network access.
4. **Group by tier**: append to `test_tier1_modules.py` or `test_tier2_modules.py`
   (or add a new tier file) and keep the module docstring's scope accurate.

## MCP Tools

This area does not expose MCP tools directly. Its capabilities are reached via
repository commands:

- Scoped run: `uv run pytest tests/unit/coverage_push/`
- Release gate: `make test` (applies the 60% coverage floor)

## Navigation

- **Self**: [PAI.md](PAI.md) — This document
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Spec**: [SPEC.md](SPEC.md)
- **Parent Directory**: [../README.md](../README.md) — Unit tests overview
- **Repository Root**: [../../../README.md](../../../README.md) — Codomyrmex
