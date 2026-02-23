# Meme Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Meme module is Codomyrmex's advanced memetic analysis engine, providing multi-layered capabilities for studying information propagation, narrative dynamics, and cultural evolution. It bridges semiotics, network theory, and computational linguistics.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

### Core Memetics

| Submodule | Classes | Purpose |
|-----------|---------|---------|
| `memetics` | `MemeticAnalyzer`, `MemeticPattern`, `MutationTracker` | Core meme analysis and mutation tracking |
| `semiotic` | `Sign`, `CodeSystem`, `Signifier`, `Signified`, `SemioticAnalyzer` | Sign theory and semiotic analysis |
| `contagion` | `ContagionModel`, `ContagionResult`, `Strain` | Information contagion and propagation modeling |
| `narrative` | `NarrativeEngine`, `StoryArc`, `NarrativeElement` | Narrative construction and analysis |

### Advanced Analysis

| Submodule | Classes | Purpose |
|-----------|---------|---------|
| `cultural_dynamics` | Cultural evolution modeling | Track cultural shift patterns |
| `swarm` | Swarm intelligence integration | Collective decision-making |
| `neurolinguistic` | Neuro-linguistic processing | Language influence modeling |
| `hyperreality` | Simulation/hyperreality analysis | Baudrillard-inspired reality layers |
| `ideoscape` | Ideological landscape mapping | Idea migration and clustering |
| `rhizome` | Non-hierarchical network analysis | Deleuze & Guattari-inspired connections |
| `epistemic` | Epistemic verification | Knowledge validation and truthfulness |

## Quick Start

```python
from codomyrmex.meme import MemeticAnalyzer, MemeticPattern, ContagionModel

# Analyze memetic patterns in content
analyzer = MemeticAnalyzer()
patterns = analyzer.detect(content="AI agents will revolutionize coding")

# Model information contagion
model = ContagionModel()
result = model.simulate(
    initial_carriers=10,
    population=1000,
    virality=0.3,
    duration=30
)
```

## Architecture

The module has 11 specialized submodules spanning sign theory, network theory, and computational linguistics. See [SPEC.md](SPEC.md) for the full architecture details.

## Navigation

- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
