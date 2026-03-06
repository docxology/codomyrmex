# Cerebrum -- Agent Integration Guide

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Agent Capabilities

The Cerebrum module provides case-based reasoning and Bayesian inference for intelligent decision-making. Agents can query the knowledge base for relevant cases and add new case references.

## Available MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `query_knowledge_base` | Query for relevant cases by feature matching | `query: str` |
| `add_case_reference` | Add a new case to the knowledge base | `case: dict` |

## Trust Level

Both MCP tools are classified as **Safe**.

## Navigation

- **Source**: [src/codomyrmex/cerebrum/](../../../../src/codomyrmex/cerebrum/)
- **Extended README**: [README.md](readme.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Parent**: [All Modules](../README.md)
