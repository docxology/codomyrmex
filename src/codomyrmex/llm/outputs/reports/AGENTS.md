# Codomyrmex Agents — src/codomyrmex/llm/outputs/reports

## Signposting
- **Parent**: [outputs](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Structured analysis reports from LLM interactions. Stores structured reports with security input length limits and other analysis metadata for debugging and analysis of LLM interactions.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `security_input_length_limits.json` – Security input length limits configuration

## Key Data

### Report Structure
- Structured reports with analysis results
- Security input length limits for safe LLM interactions
- Metadata for report analysis

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [outputs](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../../README.md) - Main project documentation