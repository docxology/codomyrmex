# Codomyrmex Agents — scripts/documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

This directory contains orchestration and utility scripts for managing documentation across the Codomyrmex project.

## Active Components

- **`orchestrate.py`** — Primary orchestrator that utilizes the `documentation` module's Python API to perform audits and quality checks.
- **`analyze_content_quality.py`** — Analyzes the quality of documentation content.
- **`audit_documentation.py`** — Performs a comprehensive audit of documentation completeness.
- **`enforce_quality_gate.py`** — Validates that documentation meets minimum quality standards.

## Operating Contracts

- Use `orchestrate.py` to perform comprehensive documentation audits and quality checks via the module API.
- Scripts should be executed from the project root or the `scripts/documentation` directory.
- The orchestrator will report an exit code of 1 if any script fails or if quality gates are not met.

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Execution | Run orchestrator to verify documentation state after changes. | TRUSTED |
| **QATester** | Execution | Run audit and quality gate scripts to verify compliance. | OBSERVED |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- **Parent**: [scripts](../README.md)
