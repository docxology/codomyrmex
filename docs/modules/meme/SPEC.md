# Meme — Functional Specification

**Module**: `codomyrmex.meme`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

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

## 2. Architecture

### Source Files

| File | Purpose |
|------|--------|
| `verify_all.py` | Verification script for the new meme module. |

### Submodule Structure

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

## 3. Dependencies

No internal Codomyrmex dependencies.

## 4. Public API

### Exports (`__all__`)

- `Meme`
- `Memeplex`
- `MemeticCode`
- `FitnessMap`
- `MemeticEngine`
- `Sign`
- `SignType`
- `DriftReport`
- `SemioticAnalyzer`
- `ContagionModel`
- `CascadeDetector`
- `PropagationTrace`
- `Cascade`
- `CascadeType`
- `ResonanceMap`
- `Narrative`
- `NarrativeArc`
- `Archetype`
- `NarrativeEngine`
- `CulturalState`
- `CulturalDynamicsEngine`
- `PowerMap`
- `SwarmAgent`
- `SwarmEngine`
- `EmergentPattern`
- `ConsensusState`
- `SwarmState`
- `CognitiveFrame`
- `BiasInstance`
- `NeurolinguisticEngine`
- `Simulacrum`
- `HyperrealityEngine`
- `SimulationLevel`
- `RealityTunnel`
- `IdeoscapeLayer`
- `IdeoscapeEngine`
- `MapFeature`
- `TerrainMap`
- `RhizomeEngine`
- `Graph`
- `Node`
- `Edge`
- `NetworkTopology`
- `EpistemicEngine`
- `EpistemicState`
- `Fact`
- `Belief`
- `Evidence`
- `CyberneticEngine`
- `ControlSystem`
- `FeedbackLoop`
- `SystemState`

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k meme -v
```

All tests follow the Zero-Mock policy.

## 6. References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/meme/)
