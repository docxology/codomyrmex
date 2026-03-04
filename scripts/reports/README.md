# Reports Scripts

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Report generation utilities for Codomyrmex, including enhanced coverage reports from pytest JSON output with HTML, Markdown, and module-by-module breakdowns.

## Purpose

These scripts process test coverage data and generate human-readable reports in multiple formats for PR reviews, CI dashboards, and module-level coverage tracking.

## Contents

| File | Description |
|------|-------------|
| `generate_coverage_report.py` | Processes `coverage.json` and generates HTML summary, Markdown PR reports, and per-module breakdowns |

## Usage

**Prerequisites:**
```bash
uv sync
uv run pytest --cov=src/codomyrmex --cov-report=json  # generates coverage.json
```

**Run:**
```bash
uv run python scripts/reports/generate_coverage_report.py --input coverage.json --output reports/
```

## Agent Usage

Agents generating coverage reports should run `pytest --cov` first to produce `coverage.json`, then invoke this script. Output can be used for PR comments or CI artifact uploads.

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent: scripts/](../README.md)
