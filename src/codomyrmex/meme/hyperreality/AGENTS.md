# Codomyrmex Agents -- src/codomyrmex/meme/hyperreality

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Purpose

Models Baudrillardian simulation theory with four levels of simulacra and Robert Anton Wilson's reality tunnels. Provides engines for creating named reality tunnels, injecting simulacra at varying simulation levels, and assessing the simulation level of objects via metadata heuristics.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `engine.py` | `HyperrealityEngine` | Orchestrator managing reality tunnels and simulacrum injection |
| `simulation.py` | `assess_reality_level` | Heuristic classification of objects into Baudrillard's four phases |
| `simulation.py` | `generate_simulacrum` | Create a simulacrum with level-appropriate fidelity and autonomy |
| `models.py` | `Simulacrum` | A copy without an original, with fidelity and autonomy scores |
| `models.py` | `SimulationLevel` | REFLECTION (1), MASK (2), ABSENCE (3), PURE (4) |
| `models.py` | `RealityTunnel` | Subjective perception filter with distortion score and active simulacra |
| `models.py` | `OntologicalStatus` | REAL, VIRTUAL, HYPERREAL, FICTIONAL |

## Operating Contracts

- `inject_simulacrum` auto-creates tunnels if the named tunnel does not exist.
- Distortion increases by `0.1 * level` per injection, capped at 1.0.
- `assess_reality_level` returns PURE (worst-case) when no provenance metadata is provided.
- Fidelity and autonomy values are preset per simulation level and not configurable.
- `get_tunnel` returns `None` for unknown names; does not raise exceptions.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: None (self-contained within `meme` package)
- **Used by**: `meme.narrative` (narratives are building blocks of reality tunnels), `meme.semiotic` (signs in hyperreality may lack referents), `meme.epistemic` (ground-truthing against hyperreal distortion)

## Navigation

- **Parent**: [meme](../README.md)
- **Root**: [Root](../../../../README.md)
