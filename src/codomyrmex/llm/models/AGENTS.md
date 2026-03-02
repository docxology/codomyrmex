# Codomyrmex Agents -- src/codomyrmex/llm/models

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides structured data models for chain-of-thought (CoT) reasoning pipelines,
including reasoning steps, traces, conclusions, and thinking depth configuration.
All types are JSON-serializable dataclasses designed for the AgentProtocol
plan-act-observe lifecycle.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `reasoning.py` | `ThinkingDepth` | Enum controlling reasoning depth: SHALLOW (1 step), NORMAL (3), DEEP (5), EXHAUSTIVE (8+) |
| `reasoning.py` | `ReasoningStep` | Single step in a CoT trace with thought, confidence, evidence, and step_type |
| `reasoning.py` | `Conclusion` | Synthesized outcome with action, justification, confidence, alternatives, and risks |
| `reasoning.py` | `ReasoningTrace` | Complete reasoning session record with steps, conclusion, duration, and token count |
| `reasoning.py` | `DEPTH_TO_STEPS` | Dict mapping ThinkingDepth enum values to target step counts |

## Operating Contracts

- Confidence values are clamped to [0.0, 1.0] in `__post_init__`.
- `ReasoningTrace.total_confidence` is a weighted blend: 70% mean step confidence + 30% conclusion confidence.
- All types support round-trip serialization via `to_dict()` / `from_dict()` and `to_json()` / `from_json()`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: stdlib `dataclasses`, `json`, `uuid`, `datetime`
- **Used by**: `agents/core/thinking_agent.py`, `llm/chain_of_thought.py`

## Navigation

- **Parent**: [llm](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
