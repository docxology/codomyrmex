# Logistics Routing -- Agent Coordination

## Purpose

Vehicle routing and path optimisation algorithms for geographic and graph-based routing problems. Provides nearest-neighbour heuristics, 2-opt improvement, Dijkstra shortest path, and A* pathfinding.

## Key Components

| Component | Role |
|-----------|------|
| `Location` | Geographic point with haversine `distance_to()` calculation |
| `RoutingConstraints` | Max distance/duration/stops, required/avoided locations, capacity, time windows |
| `Route` / `RouteStop` | Ordered stops with arrival/departure times, cumulative distance and duration |
| `RoutingAlgorithm` | ABC defining `optimize(locations, start, end, constraints)` |
| `NearestNeighborRouting` | Greedy nearest-unvisited heuristic |
| `TwoOptRouting` | 2-opt edge-swap improvement (configurable `max_iterations`, default 1000) |
| `DijkstraRouting` | Heap-based shortest path on weighted graphs (bidirectional edges) |
| `AStarRouting` | A* with Euclidean heuristic on positioned graphs |
| `create_routing_algorithm(type)` | Factory returning `NearestNeighborRouting` or `TwoOptRouting` |

## Operating Contracts

- **Haversine distance**: `Location.distance_to()` returns kilometres using Earth radius 6371 km.
- **2-opt initialisation**: `TwoOptRouting` seeds with `NearestNeighborRouting` output, then iteratively improves.
- **Graph algorithms**: `DijkstraRouting` and `AStarRouting` are standalone (not subclasses of `RoutingAlgorithm`). They operate on explicit graph structures built with `add_edge()` / `add_node()`.
- **No MCP tools**: This module does not expose MCP tools. Agents consume it as a library via Python imports.
- **Immutable inputs**: Algorithms do not modify the input `Location` list.

## Integration Points

- No external dependencies beyond the standard library (`heapq`, `math`, `random`).
- Used by `logistics/orchestration/` for spatial task scheduling.

## Navigation

- **Parent**: [logistics/](../README.md)
- **Siblings**: [orchestration/](../orchestration/AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
