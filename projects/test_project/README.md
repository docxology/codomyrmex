# test_project

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Zero-Mock reference implementation demonstrating codomyrmex capabilities. Exercises 11 integration surfaces (analysis, visualization, reporting, pipeline, agent brain, git workflow, knowledge search, security audit, MCP explorer, LLM inference) against real codomyrmex modules — no mocks, no stubs.

Run the full demonstration:

```bash
python run_demo.py
```

## Directory Contents
- `run_demo.py` – End-to-end demonstration entry point
- `src/` – 11 integration modules (agent_brain, analyzer, git_workflow, knowledge_search, llm_inference, main, mcp_explorer, pipeline, reporter, security_audit, visualizer)
- `tests/` – Zero-mock integration test suite (one file per src module)
- `config/` – YAML configuration (settings, modules, workflows)
- `data/` – Input fixtures and processed outputs
- `reports/` – Generated reports and HTML dashboards
- `pyproject.toml` – Project manifest (depends on codomyrmex editable install)
- `PAI.md`, `SPEC.md`, `AGENTS.md` – Quadruple Play documentation

## Navigation
- **Parent Directory**: [projects](../README.md)
- **Project Root**: ../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
