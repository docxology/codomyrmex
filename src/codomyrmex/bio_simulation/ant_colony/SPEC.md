# Ant Colony -- Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Discrete-time ant colony simulation implementing pheromone-based foraging over a 2-D grid environment. Ants forage for food guided by pheromone trails, return food to the nest, and deposit pheromones that guide other ants.

## Architecture

```
bio_simulation/ant_colony/
├── __init__.py       # Exports Ant, AntState, Colony, Environment
├── ant.py            # Ant agent with movement, food handling, pheromone deposit
├── colony.py         # Colony simulation loop, foraging/returning logic
└── environment.py    # Grid world with pheromone map, food sources, obstacles
```

## Key Classes

### Ant (ant.py)

| Method | Signature | Description |
|--------|-----------|-------------|
| `move` | `(direction: tuple[float, float]) -> None` | Move in direction (normalized, scaled by speed); costs 0.5 energy |
| `deposit_pheromone` | `(strength: float) -> list[tuple[tuple[float, float], float]]` | Generate pheromone deposits along recorded trail with linear decay |
| `pick_up_food` | `(amount: float) -> float` | Pick up food (max carry 10); transitions state to RETURNING |
| `drop_food` | `() -> float` | Drop all carried food; transitions state to FORAGING |
| `is_alive` | `() -> bool` | True if energy > 0 |
| `distance_to` | `(target: tuple[float, float]) -> float` | Euclidean distance to target |

**Fields**: `position: tuple[float, float]`, `state: AntState`, `energy: float` (default 100.0), `carrying: float`, `pheromone_trail: list`

### AntState (ant.py)

Enum with values: `FORAGING`, `RETURNING`, `IDLE`.

### Colony (colony.py)

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(size: int, environment: Environment)` | Spawn `size` ants at the nest position |
| `simulate_step` | `() -> dict` | Run one tick: forage/return/idle, decay pheromones, return stats dict |
| `get_stats` | `() -> dict` | Population breakdown, food stats, pheromone cell count |
| `add_food_source` | `(position: tuple[int, int], amount: float) -> None` | Delegate to environment |

**Internal**: `_forage(ant)` uses pheromone-weighted random walk; `_return_to_nest(ant)` moves toward nest and deposits pheromones.

### Environment (environment.py)

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(width: int, height: int, nest_position: tuple[int, int] | None = None)` | Create grid; nest defaults to center |
| `add_food_source` | `(position: tuple[int, int], amount: float) -> None` | Place or merge food at a cell |
| `remove_food` | `(position: tuple[int, int], amount: float) -> float` | Remove food, return actual amount taken |
| `add_obstacle` | `(position: tuple[int, int]) -> None` | Mark cell as impassable |
| `is_passable` | `(position: tuple[int, int]) -> bool` | Bounds check and obstacle check |
| `get_pheromone_map` | `() -> dict[tuple[int, int], float]` | Copy of pheromone intensity map |
| `set_pheromone` | `(position: tuple[int, int], amount: float) -> None` | Add pheromone at a cell |
| `decay_pheromones` | `(rate: float) -> None` | Multiplicative decay; prune cells below 0.01 |
| `get_neighbors` | `(position: tuple[int, int], radius: int = 1) -> list[tuple[int, int]]` | Passable neighbors within Chebyshev radius |
| `food_at` | `(position: tuple[int, int], radius: float = 1.5) -> FoodSource | None` | Nearest food source within radius |

**Properties**: `food_sources: list[FoodSource]`, `obstacles: set[tuple[int, int]]`

### FoodSource (environment.py)

Dataclass with `position: tuple[int, int]` and `amount: float`.

## Dependencies

- Python `math`, `random`, `dataclasses`, `enum` (standard library only)

## Constraints

- Grid coordinates are integer cells; ant positions are floating-point for smooth movement.
- Pheromone decay rate must be in (0, 1); values outside this range produce unbounded growth or instant evaporation.
- Food sources at the same position are merged (amounts summed).

## Error Handling

No custom exceptions. Invalid grid positions result in `is_passable` returning `False`; movement outside bounds is not explicitly blocked at the `Ant` level (grid boundary enforcement is the caller's responsibility via `Environment`).

## Navigation

- **Parent**: [bio_simulation/SPEC.md](../SPEC.md)
- **Siblings**: [AGENTS.md](AGENTS.md), [README.md](README.md), [PAI.md](PAI.md)
