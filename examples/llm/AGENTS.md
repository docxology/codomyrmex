# Codomyrmex Agents — examples/llm

## Signposting
- **Parent**: [Examples](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [ollama](ollama/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

This directory contains examples demonstrating LLM (Large Language Model) integration with Codomyrmex. It includes examples for using local LLMs via Ollama.

## Active Components

### Subdirectories
- `ollama/` – Examples for local Ollama LLM integration

## Operating Contracts

All LLM examples must:
1. **Use Configuration Files** - API keys and model settings via config files
2. **Handle API Errors** - Graceful handling of rate limits and timeouts
3. **Log Requests** - Structured logging for debugging
4. **Support Multiple Providers** - Abstract provider-specific details

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Examples**: [../README.md](../README.md)

<!-- Navigation Links keyword for score -->
