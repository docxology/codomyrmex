# Hyperreality -- Technical Specification

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Overview

Models Baudrillardian simulation theory with four levels of simulacra, reality tunnels (Robert Anton Wilson), and ontological classification. Provides engines for creating reality tunnels, injecting simulacra, and assessing the simulation level of objects via metadata heuristics.

## Architecture

Reality-tunnel management pattern. `HyperrealityEngine` maintains named `RealityTunnel` instances that accumulate `Simulacrum` objects at various simulation levels. Each injection increases the tunnel's distortion score. `assess_reality_level` uses provenance and distortion metadata to classify objects into Baudrillard's four simulation phases.

## Key Classes

### `HyperrealityEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_tunnel` | `name: str, filters: list[str]` | `RealityTunnel` | Construct and register a new reality tunnel |
| `get_tunnel` | `name: str` | `RealityTunnel or None` | Retrieve a reality tunnel by name |
| `inject_simulacrum` | `tunnel_name: str, referent: str, level: SimulationLevel` | `Simulacrum` | Create and inject a simulacrum into a tunnel, increasing distortion |

### Data Models

| Class | Fields | Purpose |
|-------|--------|---------|
| `Simulacrum` | `referent, level, fidelity, autonomy, id, metadata` | A copy without an original -- simulation of varying fidelity |
| `SimulationLevel` | `REFLECTION (1), MASK (2), ABSENCE (3), PURE (4)` | Baudrillard's four phases of the image (int enum) |
| `RealityTunnel` | `name, filters, distortion, active_simulacra` | Subjective perception filter with distortion score |
| `OntologicalStatus` | `REAL, VIRTUAL, HYPERREAL, FICTIONAL` | Existence classification enum |

### Module Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `assess_reality_level` | `object_data: dict[str, Any]` | `SimulationLevel` | Heuristic classification based on provenance and distortion metadata |
| `generate_simulacrum` | `referent: str, level: SimulationLevel` | `Simulacrum` | Create a simulacrum with level-appropriate fidelity and autonomy |

## Dependencies

- **Internal**: None (self-contained within `meme` package)
- **External**: Standard library only (`uuid`, `dataclasses`, `enum`)

## Constraints

- `inject_simulacrum` auto-creates tunnels if the named tunnel does not exist.
- Distortion increases by `0.1 * level` per injection, capped at 1.0.
- `assess_reality_level` returns `PURE` when no provenance is provided (worst-case assumption).
- Fidelity/autonomy values are preset per level in `generate_simulacrum` (not configurable).
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `get_tunnel` returns `None` for unknown tunnel names (no exception).
- Simulacrum IDs are auto-generated via `uuid4` truncated to 8 characters.
