# Logistics Routing -- Functional Specification

## Overview

Vehicle routing and graph pathfinding algorithms. All code lives in `__init__.py` with no sub-modules.

## Key Classes

### `Location`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier |
| `name` | `str` | Display name |
| `latitude` | `float` | Geographic latitude |
| `longitude` | `float` | Geographic longitude |
| `metadata` | `dict[str, Any]` | Arbitrary metadata |

Method: `distance_to(other: Location) -> float` -- haversine distance in kilometres (Earth radius = 6371 km).

### `RoutingConstraints`

| Field | Type | Default |
|-------|------|---------|
| `max_distance` | `float \| None` | `None` (km) |
| `max_duration` | `float \| None` | `None` (minutes) |
| `max_stops` | `int \| None` | `None` |
| `required_stops` | `list[str]` | `[]` |
| `avoid_locations` | `list[str]` | `[]` |
| `vehicle_capacity` | `float \| None` | `None` |
| `time_windows` | `dict[str, tuple[int, int]]` | `{}` |

### `Route` / `RouteStop`

`Route` accumulates stops via `add_stop(location, distance_from_prev, service_time, load, speed)` with default speed 50 km/h. Tracks `total_distance`, `total_duration`, `total_load`. `to_dict()` serialises to JSON-compatible format.

### `RoutingAlgorithm` (ABC)

Abstract method: `optimize(locations, start, end=None, constraints=None) -> Route`.

### `NearestNeighborRouting`

Greedy nearest-unvisited heuristic. O(n^2) distance comparisons. Optionally returns to `end` if specified.

### `TwoOptRouting`

Initialises from `NearestNeighborRouting` output. Iteratively performs 2-opt edge swaps until no improvement or `max_iterations` (default 1000) reached. Breaks on first improvement per iteration (first-improvement strategy).

### `DijkstraRouting`

Heap-based shortest path on weighted graphs.

| Method | Description |
|--------|-------------|
| `add_edge(from_id, to_id, distance, bidirectional=True)` | Add weighted edge |
| `shortest_path(start_id, end_id) -> (path, distance)` | Return shortest path and total distance |

Returns `([], inf)` for unreachable nodes.

### `AStarRouting`

A* pathfinding with Euclidean heuristic on positioned graphs.

| Method | Description |
|--------|-------------|
| `add_node(node_id, x, y)` | Add node with 2D position |
| `add_edge(from_id, to_id, cost=None)` | Add edge (defaults to Euclidean distance) |
| `find_path(start_id, goal_id) -> (path, cost)` | Return optimal path and total cost |

### `create_routing_algorithm(algorithm_type, **kwargs)`

Factory function. Supported types: `"nearest_neighbor"`, `"two_opt"`. Raises `ValueError` for unknown types. `DijkstraRouting` and `AStarRouting` are not included (different interface).

## Dependencies

Standard library only: `heapq`, `math`, `random`, `abc`, `dataclasses`, `enum`.

## Constraints

- `DijkstraRouting` and `AStarRouting` do not implement the `RoutingAlgorithm` ABC (different method signatures).
- `NearestNeighborRouting` and `TwoOptRouting` share the `optimize()` interface and are interchangeable via the factory.
- Haversine formula assumes spherical Earth.

## Navigation

- **Specification**: This file
- **Agent coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [logistics/](../SPEC.md)
