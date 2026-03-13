# Agent Planner

**Module**: `codomyrmex.agents.planner` | **Category**: Core Infrastructure | **Last Updated**: March 2026

## Overview

Hierarchical goal decomposition and convergent planning-execution-feedback system. Breaks goals into structured task trees, executes with progress tracking, and re-plans via memory-enriched context.

## Purpose

Hierarchical goal decomposition and convergent planning-execution-feedback system. Breaks high-level goals into structured task trees, executes them with progress tracking, scores quality across four dimensions, and re-plans using memory-enriched context until convergence.

## Source Module Structure

Source: [`src/codomyrmex/agents/planner/`](../../../../src/codomyrmex/agents/planner/)

### Key Files

| File | Purpose |
|:---|:---|
| [executor.py](../../../../src/codomyrmex/agents/planner/executor.py) |  |
| [feedback_config.py](../../../../src/codomyrmex/agents/planner/feedback_config.py) |  |
| [feedback_loop.py](../../../../src/codomyrmex/agents/planner/feedback_loop.py) |  |
| [plan_engine.py](../../../../src/codomyrmex/agents/planner/plan_engine.py) |  ⭐ |
| [plan_evaluator.py](../../../../src/codomyrmex/agents/planner/plan_evaluator.py) |  ⭐ |

## Quick Start

```python
from codomyrmex.agents.planner import PlannerClient

client = PlannerClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [planner/README.md](../../../../src/codomyrmex/agents/planner/README.md) |
| SPEC | [planner/SPEC.md](../../../../src/codomyrmex/agents/planner/SPEC.md) |
| AGENTS | [planner/AGENTS.md](../../../../src/codomyrmex/agents/planner/AGENTS.md) |
| PAI | [planner/PAI.md](../../../../src/codomyrmex/agents/planner/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/planner/](../../../../src/codomyrmex/agents/planner/)
- **Project Root**: [README.md](../../../README.md)
