# Meme Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive framework for modeling, analyzing, and engineering the propagation, mutation, and evolution of information units (memes) through cultural, cognitive, and network substrates. Organized into 12 specialized submodules across 6 phases.

## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **Memetic Engine** -- Core `Meme`, `Memeplex`, fitness landscapes, and genetic operators.
- **Contagion Models** -- Epidemiological models (SIR, SIS, SEIR) and cascade detection.
- **Narrative Engine** -- Computational narratology with arcs, archetypes, and myth generation.
- **Swarm Intelligence** -- Flocking algorithms, consensus mechanisms, emergent pattern detection.
- **Epistemic Mapping** -- Truth verification, knowledge warfare, facts, beliefs, and evidence.
- **Cybernetic Control** -- Feedback loops, homeostatic regulation, and autonomic control.

## Submodules

| Submodule | Phase | Description |
|-----------|-------|-------------|
| `memetics` | Core | Meme, Memeplex, fitness, mutation |
| `semiotic` | Core | Signs, encoding, drift |
| `contagion` | Propagation | Cascade and epidemic propagation models |
| `narrative` | Propagation | Narrative arcs, myths, archetypes |
| `cultural_dynamics` | Dynamics | Cultural oscillation, zeitgeist, power maps |
| `swarm` | Dynamics | Swarm intelligence and consensus |
| `neurolinguistic` | Dynamics | Cognitive framing and bias |
| `hyperreality` | Topology | Simulacra and reality tunnels |
| `ideoscape` | Topology | Ideational ecosystem ecology |
| `rhizome` | Topology | Rhizomatic network analysis |
| `epistemic` | Truth | Epistemic territory and knowledge warfare |
| `cybernetic` | Control | Feedback loops and control systems |

## Quick Start

```python
from codomyrmex.meme import MemeticEngine, Meme

engine = MemeticEngine()
memes = engine.dissect("The quick brown fox jumps over the lazy dog.")
for meme in memes:
    print(f"Meme: {meme.content}, Fitness: {meme.fitness}")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k meme -v
```

## Navigation

- **Source**: [src/codomyrmex/meme/](../../../src/codomyrmex/meme/)
- **API Spec**: [API_SPECIFICATION.md](../../../src/codomyrmex/meme/API_SPECIFICATION.md)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/meme/MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Modules](../README.md)
