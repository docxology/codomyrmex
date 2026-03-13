# Meta-Agent System

**Module**: `codomyrmex.agents.meta` | **Category**: Core Infrastructure | **Last Updated**: March 2026

## Overview

Meta-level agent capabilities including self-reflection, capability assessment, strategy selection, and meta-cognitive monitoring. Agents that reason about agents.

## Purpose

Self-improving meta-agent subsystem that tracks agent task outcomes across four dimensions and evolves strategy selection using success-rate tracking and A/B testing. Designed as a pluggable wrapper around any task function.

## Source Module Structure

Source: [`src/codomyrmex/agents/meta/`](../../../../src/codomyrmex/agents/meta/)

### Key Files

| File | Purpose |
|:---|:---|
| [ab_testing.py](../../../../src/codomyrmex/agents/meta/ab_testing.py) |  |
| [meta_agent.py](../../../../src/codomyrmex/agents/meta/meta_agent.py) |  ⭐ |
| [scoring.py](../../../../src/codomyrmex/agents/meta/scoring.py) |  |
| [strategies.py](../../../../src/codomyrmex/agents/meta/strategies.py) |  |

## Quick Start

```python
from codomyrmex.agents.meta import MetaClient

client = MetaClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [meta/README.md](../../../../src/codomyrmex/agents/meta/README.md) |
| SPEC | [meta/SPEC.md](../../../../src/codomyrmex/agents/meta/SPEC.md) |
| AGENTS | [meta/AGENTS.md](../../../../src/codomyrmex/agents/meta/AGENTS.md) |
| PAI | [meta/PAI.md](../../../../src/codomyrmex/agents/meta/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/meta/](../../../../src/codomyrmex/agents/meta/)
- **Project Root**: [README.md](../../../README.md)
