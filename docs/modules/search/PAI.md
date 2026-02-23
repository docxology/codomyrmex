# Personal AI Infrastructure — Search Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Search module provides code pattern identification, full-text search, and fuzzy matching for codebase exploration. It powers the PAI Algorithm's OBSERVE phase by enabling agents to find relevant code, patterns, and documentation across the project.

## PAI Capabilities

### Code Search

- Regex-based pattern search across source files
- File type filtering (Python, JavaScript, Markdown, etc.)
- Result ranking by relevance
- Context-aware snippet extraction

### Fuzzy Matching

- Approximate string matching for typo-tolerant search
- File path fuzzy matching for navigation
- Symbol name fuzzy matching for codebase exploration

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| Search functions | Various | Pattern matching, full-text, fuzzy search |

## PAI Algorithm Phase Mapping

| Phase | Search Contribution |
|-------|----------------------|
| **OBSERVE** | Find relevant code, files, and patterns in the codebase |
| **THINK** | Search results inform reasoning about relevant context |
| **VERIFY** | Search for potential issues and verify completeness of changes |

## MCP Integration

The `search_code` MCP tool is powered by this module — regex search across code files with type filtering.

## Architecture Role

**Core Layer** — Primary codebase exploration tool consumed by all agent types. Used by `agents/` (Explore subagent), `documents/` (content search), and MCP `search_code` tool.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
