# Codomyrmex Agents — docs/development

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent coordination for developer-facing guides: environment, testing, documentation standards, multi-agent Git, uv usage, and local PR/SARIF triage.

## Contents (by file)

| File | Role |
|:---|:---|
| [documentation.md](documentation.md) | Doc standards, AGENTS/README/SPEC parity, Mermaid |
| [environment-setup.md](environment-setup.md) | Prerequisites and configuration |
| [testing-strategy.md](testing-strategy.md) | Zero-mock policy, coverage expectations, layout |
| [uv-usage-guide.md](uv-usage-guide.md) | uv workflows |
| [multi-agent-git.md](multi-agent-git.md) | Concurrent agent Git practices |
| [google-integration.md](google-integration.md) | Google Cloud / Workspace for dev |
| [code-review-and-sarif.md](code-review-and-sarif.md) | `scripts/review/` helpers, Bandit SARIF artifacts, sarif-tools |
| [README.md](README.md) | Section index |
| [SPEC.md](SPEC.md), [PAI.md](PAI.md) | Local specs / PAI notes |

## Operating contracts

- Prefer measured commands (`uv run pytest`, `uv run ruff`) over hand-waved thresholds; point to `pyproject.toml` for gates.
- New automation that contributors run locally should be linked from [README.md](README.md) and, when security-related, from [code-review-and-sarif.md](code-review-and-sarif.md).

## Navigation

- **Parent**: [docs/AGENTS.md](../AGENTS.md), [docs/README.md](../README.md)
- **Project root**: [README.md](../../README.md), [AGENTS.md](../../AGENTS.md)
