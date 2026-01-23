# Codomyrmex Agents — projects/test_project/data

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: January 2026

## Signposting

- **Parent**: [test_project/AGENTS.md](../AGENTS.md)
- **Self**: [data/AGENTS.md](AGENTS.md)
- **Key Artifacts**: `input/sample_data.json`

## Purpose

Data storage layer providing input files and processed output directories for the test_project pipeline.

## Active Components

| Directory/File | Purpose |
| :--- | :--- |
| `input/` | Source data files for analysis |
| `input/sample_data.json` | Sample analysis data |
| `processed/` | Intermediate and cached results |

## Operating Contracts

### Data Handling

- Input files are read-only during analysis
- Processed outputs may be overwritten on re-runs
- JSON format for structured data
- UTF-8 encoding for all text files

### Cleanup

- Processed directory can be cleared for fresh runs
- Input data should remain stable

## Navigation Links

- **📁 Parent**: [../AGENTS.md](../AGENTS.md)
- **🏠 Project Root**: [../../README.md](../../README.md)
