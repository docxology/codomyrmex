# Personal AI Infrastructure -- Meme Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Meme module is a **comprehensive information dynamics framework** that models, analyzes, and engineers the propagation, mutation, and evolution of information units (memes) through cultural, cognitive, and network substrates. It treats ideas as living entities subject to evolutionary pressures, epidemiological spread, narrative structuring, and cybernetic control. The module spans 12 submodules organized into 5 functional phases.

## PAI Capabilities

### Memetic Analysis

Dissect text into memes and analyze fitness:

```python
from codomyrmex.meme import MemeticEngine, Meme

engine = MemeticEngine()
memes = engine.dissect("The quick brown fox jumps over the lazy dog.")
for meme in memes:
    print(f"Meme: {meme.content}, Fitness: {meme.fitness}")
```

### Contagion Modeling

Simulate information spread using epidemiological models:

```python
from codomyrmex.meme.contagion import SIRModel, run_simulation

model = SIRModel(population=10000, initial_infected=10, beta=0.3, gamma=0.1)
results = run_simulation(model, steps=100)
```

### Narrative Engineering

Build and analyze narrative structures:

```python
from codomyrmex.meme.narrative import NarrativeEngine, heros_journey_arc

engine = NarrativeEngine()
arc = heros_journey_arc()
```

### Epistemic Verification

Verify claims against evidence:

```python
from codomyrmex.meme.epistemic import EpistemicEngine, verify_claim, Fact, Evidence

fact = Fact(claim="The module has 12 submodules")
evidence = Evidence(source="__init__.py", content="12 imports")
result = verify_claim(fact, evidence)
```

### Cybernetic Control

Model feedback loops and control systems:

```python
from codomyrmex.meme.cybernetic import CyberneticEngine, PIDController

controller = PIDController(kp=1.0, ki=0.1, kd=0.01)
engine = CyberneticEngine()
```

## Key Exports

| Export | Submodule | Type | Purpose |
|--------|-----------|------|---------|
| `Meme` | memetics | Class | Discrete replicable information unit |
| `Memeplex` | memetics | Class | Co-adapted complex of memes |
| `MemeticEngine` | memetics | Class | Core dissection and fitness analysis engine |
| `Sign` | semiotic | Class | Semiotic sign with signifier/signified |
| `SemioticAnalyzer` | semiotic | Class | Sign relationship and drift analysis |
| `ContagionModel` | contagion | Class | Base epidemiological contagion model |
| `CascadeDetector` | contagion | Class | Information cascade detection |
| `Narrative` | narrative | Class | Complete narrative structure |
| `NarrativeEngine` | narrative | Class | Narrative analysis and generation |
| `CulturalDynamicsEngine` | cultural_dynamics | Class | Cultural trend simulation |
| `SwarmEngine` | swarm | Class | Swarm intelligence simulation |
| `NeurolinguisticEngine` | neurolinguistic | Class | Cognitive framing and bias analysis |
| `HyperrealityEngine` | hyperreality | Class | Simulacra and reality tunnel modeling |
| `IdeoscapeEngine` | ideoscape | Class | Information terrain cartography |
| `RhizomeEngine` | rhizome | Class | Rhizomatic network analysis |
| `EpistemicEngine` | epistemic | Class | Truth verification and knowledge warfare |
| `CyberneticEngine` | cybernetic | Class | Feedback loop and control system modeling |

## PAI Algorithm Phase Mapping

| Phase | Meme Module Contribution |
|-------|-------------------------|
| **OBSERVE** | `SemioticAnalyzer` decodes sign-meaning relationships; `EpistemicEngine` maps what is known vs believed; `CascadeDetector` observes information flow patterns |
| **PLAN** | `NarrativeEngine` structures communication plans around proven arc templates; `IdeoscapeEngine` maps the terrain of ideas to identify strategic positions |
| **EXECUTE** | `MemeticEngine` generates and mutates memes; `SwarmEngine` coordinates collective action; `CyberneticEngine` applies control signals |
| **VERIFY** | `EpistemicEngine.verify_claim()` validates factual claims against evidence; `HyperrealityEngine` assesses simulation levels to detect information drift from reality |
| **LEARN** | `CulturalDynamicsEngine` tracks cultural evolution; `NeurolinguisticEngine` identifies cognitive biases; `RhizomeEngine` maps network topology changes over time |

## Submodule Architecture

```
codomyrmex.meme
  Phase 1 (Core)        memetics, semiotic
  Phase 2 (Propagation) contagion, narrative
  Phase 3 (Dynamics)    cultural_dynamics, swarm, neurolinguistic
  Phase 4 (Topology)    hyperreality, ideoscape, rhizome
  Phase 5 (Control)     epistemic, cybernetic
```

## Architecture Role

**Application Layer** -- Advanced domain-specific module for information dynamics and memetic analysis. Self-contained with no upward dependencies. Each submodule is independently usable while the top-level `__init__.py` re-exports 50+ classes for unified access.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.meme import ...`
- CLI: `codomyrmex meme <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md)
