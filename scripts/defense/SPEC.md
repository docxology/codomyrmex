# Defense Module Demos Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Demonstrates the defense module capabilities including rate limiting, detection rules, active defense triggers, and rabbit hole engagement for adversarial interaction.

## Functional Requirements

- **demo_orchestrator.py**: Runs defense pipeline demos with rate limiting, SQL injection detection rules, and RabbitHole engagement


## Execution

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
uv run python scripts/defense/demo_orchestrator.py
```

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md)
