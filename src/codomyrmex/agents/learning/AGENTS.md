# Agent Learning Agents

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Meta-agents responsible for training and improving the workforce agents.

## Agents

### `CoachAgent` (Reflection)

- **Role**: Reviews performance and provides feedback.
- **Capabilities**: `review_logs`, `suggest_improvement`.

### `SkillMiner` (Skills)

- **Role**: Extracts reusable code and logic from successful tasks.
- **Capabilities**: `mine_skill`, `catalog_function`.

### `TrainerAgent` (Curriculum)

- **Role**: Generates practice scenarios.
- **Capabilities**: `create_scenario`, `evaluate_performance`.

## Tools

| Tool | Agent | Description |
| :--- | :--- | :--- |
| `analyze_trace` | CoachAgent | Parse execution history |
| `extract_function` | SkillMiner | Save code snippet as skill |

## Integration

These agents integrate with `codomyrmex.agents.core` and use the MCP protocol for tool access.

## Navigation

- [README](README.md) | [SPEC](SPEC.md)
