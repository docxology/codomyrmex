# Meme Module — Agent Coordination

## Purpose

codomyrmex.meme — Unified Memetic Warfare & Information Dynamics Module.

A comprehensive framework for modeling, analyzing, and engineering the
propagation, mutation, and evolution of information units (memes) through
cultural, cognitive, and network substrates.

Submodules
----------
memetics        Core memetic engine — Meme, Memeplex, fitness, mutation.
semiotic        Computational semiotics — signs, encoding, drift.
contagion       Information cascade & epidemic propagation models.
narrative       Computational narratology — arcs, myths, insurgency.
cultural_dynamics  Cultural oscillation, zeitgeist, power dynamics.
hyperreality    Baudrillardian simulacra & consensus engineering.
swarm           Swarm intelligence — ACO, PSO, stigmergy, emergence.
neurolinguistic Cognitive framing, bias exploitation, metacognition.
ideoscape       Ideational ecosystem ecology — Lotka-Volterra for ideas.
rhizome         Rhizomatic network analysis — plateaus, lines of flight.
epistemic       Epistemic territory mapping & knowledge warfare.
cybernetic      Cybernetic control theory & feedback engineering.

## Key Capabilities

- **`Meme`** — Available export
- **`Memeplex`** — Available export
- **`MemeticCode`** — Available export
- **`FitnessMap`** — Available export
- **`MemeticEngine`** — Available export
- **`Sign`** — Available export
- **`SignType`** — Available export
- **`DriftReport`** — Available export

## Agent Usage Patterns

```python
from codomyrmex.meme import MemeticEngine, Meme

# Initialize engine
engine = MemeticEngine()

# Dissect text into memes
text = "The quick brown fox jumps over the lazy dog."
memes = engine.dissect(text)

# Analyze fitness
for meme in memes:
    print(f"Meme: {meme.content}, Fitness: {meme.fitness}")
```

## Key Components

| Export | Type |
|--------|------|
| `Meme` | Public API |
| `Memeplex` | Public API |
| `MemeticCode` | Public API |
| `FitnessMap` | Public API |
| `MemeticEngine` | Public API |
| `Sign` | Public API |
| `SignType` | Public API |
| `DriftReport` | Public API |
| `SemioticAnalyzer` | Public API |
| `ContagionModel` | Public API |
| `CascadeDetector` | Public API |
| `PropagationTrace` | Public API |
| `Cascade` | Public API |
| `CascadeType` | Public API |
| `ResonanceMap` | Public API |

## Source Files

| File | Description |
|------|-------------|
| `verify_all.py` | Verification script for the new meme module. |

## Submodules

- `contagion/` — Contagion
- `cultural_dynamics/` — Cultural Dynamics
- `cybernetic/` — Cybernetic
- `epistemic/` — Epistemic
- `hyperreality/` — Hyperreality
- `ideoscape/` — Ideoscape
- `memetics/` — Memetics
- `narrative/` — Narrative
- `neurolinguistic/` — Neurolinguistic
- `rhizome/` — Rhizome
- `semiotic/` — Semiotic
- `swarm/` — Swarm

## Integration Points

- **Docs**: [Module Documentation](../../../docs/modules/meme/README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k meme -v
```

- Always use real, functional tests — no mocks (Zero-Mock policy)
- Verify all changes pass existing tests before submitting
