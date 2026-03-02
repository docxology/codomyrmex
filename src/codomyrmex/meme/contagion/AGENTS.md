# Codomyrmex Agents -- src/codomyrmex/meme/contagion

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Purpose

Models the spread of information using compartmental epidemic models (SIR, SIS, SEIR) adapted for memetic propagation. Detects and classifies information cascades from event streams by velocity and size, and provides simulation runners for contagion scenarios.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `epidemic.py` | `SIRModel` | Susceptible-Infected-Recovered simulation for meme spread |
| `epidemic.py` | `SISModel` | Susceptible-Infected-Susceptible loop for recurring trends |
| `epidemic.py` | `SEIRModel` | Adds Exposed incubation stage for memes requiring priming |
| `cascade.py` | `CascadeDetector` | Detects and classifies cascades from event dicts |
| `cascade.py` | `detect_cascades` | Convenience wrapper for `CascadeDetector.detect` |
| `models.py` | `PropagationTrace` | Simulation output with per-step S/I/R counts |
| `models.py` | `Cascade` | Detected cascade event with velocity and type |
| `models.py` | `CascadeType` | Classification: VIRAL, ORGANIC, MANUFACTURED, DAMPENED |
| `models.py` | `ContagionModel` | Configuration dataclass (beta, gamma, network_size) |
| `simulation.py` | `run_simulation` | High-level runner wrapping SIRModel with topology param |

## Operating Contracts

- Simulations use mean-field approximation; no explicit network structure.
- Small changes in `infection_rate` (beta) can drastically alter outcomes; run sensitivity analyses.
- `run_simulation` accepts a `topology` parameter for future expansion but currently uses mean-field only.
- Cascade classification uses fixed thresholds: velocity >10.0 = VIRAL, size <5 = DAMPENED.
- Events passed to `CascadeDetector.detect` must include `meme_id`, `node_id`, and `timestamp` keys.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: None (self-contained within `meme` package)
- **Used by**: `meme.swarm` (contagion dynamics parameterize swarm behavior), `meme.rhizome` (network-based simulation expansion)

## Navigation

- **Parent**: [meme](../README.md)
- **Root**: [Root](../../../../README.md)
