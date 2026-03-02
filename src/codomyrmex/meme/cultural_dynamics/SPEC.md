# Cultural Dynamics -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Models cultural systems as dynamical systems with spectral analysis of cultural oscillations, zeitgeist trajectory construction from signal streams, mutation probability estimation, and power topology mapping from interaction graphs.

## Architecture

Engine-and-models pattern: `CulturalDynamicsEngine` operates on immutable dataclass models (`CulturalState`, `Signal`, `Trajectory`, `FrequencyMap`, `PowerMap`). The engine is stateless -- all state flows through the model objects.

## Key Classes

### `CulturalDynamicsEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `oscillation_spectrum` | `time_series: list[CulturalState], dimension: str` | `FrequencyMap` | Spectral analysis estimating dominant frequency, period, and amplitude |
| `zeitgeist_trajectory` | `signals: list[Signal]` | `Trajectory` | Aggregate signals via exponential moving average into state sequence |
| `mutation_probability` | `state: CulturalState, perturbation: Meme` | `float` | Probability (0.0-0.9) based on state energy |
| `power_topology` | `nodes: list[str], interactions: list[tuple]` | `PowerMap` | Degree-centrality power mapping from interaction pairs |

### Data Models

| Class | Key Fields | Description |
|-------|-----------|-------------|
| `CulturalState` | `dimensions: dict[str, float]`, `momentum`, `energy`, `timestamp` | Snapshot of cultural dimensions (-1 to 1) |
| `Signal` | `source`, `content`, `strength`, `valence`, `dimension`, `timestamp` | Discrete cultural signal event |
| `Trajectory` | `states: list[CulturalState]`, `trend_vector` | Temporal sequence of cultural states |
| `FrequencyMap` | `dimension`, `dominant_frequency`, `period`, `amplitude` | Spectral analysis result |
| `PowerMap` | `nodes: list[str]`, `centrality_scores: dict[str, float]` | Power dynamics mapping |

## Dependencies

- **Internal**: `codomyrmex.meme.memetics.models` (Meme dataclass)
- **External**: None (stdlib only)

## Constraints

- `CulturalState.dimensions` values should be in the range [-1, 1] by convention.
- `mutation_probability` is capped at 0.9 via `min(0.9, ...)`.
- `zeitgeist_trajectory` sorts signals by timestamp and applies exponential moving average with alpha=0.1.
- Zero-mock: real computations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `oscillation_spectrum` returns a zero-valued `FrequencyMap` for empty time series.
- All errors logged before propagation.
