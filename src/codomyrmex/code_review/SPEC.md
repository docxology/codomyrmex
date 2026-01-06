# code_review - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Automates code quality assessment. It combines static analysis results with LLM-based semantic review to provide actionable feedback.

## Design Principles
- **Hybrid Analysis**: Use deterministic tools (linters) for syntax, and probabilistic models (LLMs) for semantics.
- **Actionable**: Feedback must identify location (line number) and suggestion.

## Functional Requirements
1.  **Analysis**: Run configured checks on diffs.
2.  **Reporting**: Aggregate findings into a structured report.

## Interface Contracts
- `CodeReview`: Main facade.
- `QualityGates`: Threshold logic (e.g., "Block if critical severity").

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)
