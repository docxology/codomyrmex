# examples

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Reference workflow definitions (see [../README.md](../README.md) for the
format). They are not loaded by default; point a manager at this directory
(`WorkflowManager(config_dir=Path("config/workflows/examples"))`) or copy a
file into `config/workflows/production/` to run one. No step changes the
files in the directory the workflow runs in (linters may write their caches).

## Directory Contents

- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `basic-analysis.json` – validate the environment, then static analysis
- `code-analysis-pipeline.json` – static analysis, analysis-tool inventory and secret scan
- `complex-analysis.json` – fan-out/fan-in dependency example (analysis, secrets, docs, report)
- `sample_analysis_workflow.json` – in-memory chart of static data, docs check, secret scan, report

## Navigation

- **Parent Directory**: [workflows](../README.md)
- **Project Root**: ../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
