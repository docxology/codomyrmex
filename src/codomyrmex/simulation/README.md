# Simulation Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Simulation module provides a general-purpose agent-based simulation engine.
It supports configurable simulation parameters, a step-based execution loop,
multiple agent types (random, rule-based, and Q-learning), and result collection
for modeling complex systems. The `Simulator.run` method is exposed as an MCP
tool for PAI integration.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Simulator` | Class | Core simulation engine with step loop, agent management, and environment state |
| `SimulationConfig` | Dataclass | Configuration: name, max_steps, seed, custom params dict |

## Core Classes

### Simulator

The engine that drives the simulation loop. Each step follows a three-phase cycle:

1. **Act** -- Every agent receives an observation of the environment and returns an `Action`.
2. **Update** -- The environment state is updated based on all agent actions.
3. **Learn** -- Each agent receives a reward signal and updates its internal state.

```python
from codomyrmex.simulation import Simulator, SimulationConfig
from codomyrmex.simulation.agent import RandomAgent

config = SimulationConfig(name="demo", max_steps=100, seed=42)
agent = RandomAgent("agent_1", action_types=["move", "wait", "observe"])

sim = Simulator(config, agents=[agent])
results = sim.run()

print(results.steps_completed)  # 100
print(results.status)           # "completed"
print(results.agent_count)      # 1
```

### SimulationConfig

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `name` | `str` | `"default_simulation"` | Simulation identifier |
| `max_steps` | `int` | `1000` | Maximum number of steps before termination |
| `seed` | `int \| None` | `None` | Random seed for reproducibility |
| `params` | `dict[str, Any]` | `{}` | Arbitrary custom parameters |

### SimulationResult

Returned by `Simulator.run()` and `Simulator.get_results()`:

| Field | Type | Content |
|-------|------|---------|
| `steps_completed` | `int` | Number of steps executed |
| `config_name` | `str` | Name from the config |
| `status` | `str` | `"completed"` or `"running"` |
| `agent_count` | `int` | Number of agents in the simulation |
| `history` | `list[dict]` | Environment state snapshots |

## Agent Types

All agents extend the abstract `Agent` base class defined in `agent.py`.

| Agent | Strategy | Use Case |
|-------|----------|----------|
| `RandomAgent` | Uniform random action selection | Baselines, stress testing |
| `RuleBasedAgent` | Priority-ordered condition-action rules | Deterministic policies, guard behaviors |
| `QLearningAgent` | Tabular Q-learning with epsilon-greedy exploration | Adaptive learning, reinforcement learning experiments |

### Agent Lifecycle

Every agent implements:

- `act(observation) -> Action` -- Decide what to do given current state (abstract, required)
- `learn(reward) -> None` -- Update internal state from reward signal (optional override)
- `reset() -> None` -- Reset step count and action history
- `record_action(action) -> None` -- Append action to history
- `to_dict() -> dict` -- Serialize agent state

## Architecture

```
simulation/
  __init__.py     # Exports: Simulator, SimulationConfig
  simulator.py    # Simulator, SimulationConfig, SimulationResult, MCP tool
  agent.py        # Agent (ABC), Action, RandomAgent, RuleBasedAgent, QLearningAgent
  tests/          # Zero-mock tests
```

## Integration with Other Modules

| Module | Integration |
|--------|------------|
| `logging_monitoring` | Simulator logs step progress, agent errors, and completion via `get_logger` |
| `model_context_protocol` | `Simulator.run` is decorated with `@mcp_tool` for PAI access |
| `bio_simulation` | The bio_simulation module provides domain-specific ant colony simulations that follow similar agent patterns |

## Navigation

- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
