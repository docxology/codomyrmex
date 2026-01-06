# pattern_matching - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `pattern_matching` module provides code analysis through AST parsing, pattern recognition, and embedding generation for semantic search and similarity.

## Design Principles

### Functionality
- **Multi-Step Pipeline**: Parse -> Recognize -> Embed -> Analyze.
- **Configurable Patterns**: Rules for patterns (e.g., code smells) are defined externally.

## Functional Requirements

1.  **AST Parsing**: Convert source code to a syntax tree.
2.  **Symbol Extraction**: Identify functions, classes, imports.
3.  **Embedding**: Generate vector representations for semantic tasks.

## Interface Contracts

- `run_codomyrmex_analysis.py`: Main CLI and entry point.
- Output: JSON files with structured analysis.

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)

- **Parent**: [../SPEC.md](../SPEC.md)
