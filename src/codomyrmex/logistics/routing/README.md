# Routing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Logistics routing algorithms. Provides implementations for vehicle routing and path optimization including nearest neighbor heuristics, 2-opt improvement, Dijkstra shortest path, and A* pathfinding.

## Key Exports

- **`Location`** -- A geographic location dataclass with haversine distance calculation between points
- **`RoutingConstraints`** -- Constraint parameters for route optimization (max distance, duration, stops, capacity, time windows)
- **`RouteStop`** -- A single stop within a route, tracking arrival/departure times and load
- **`Route`** -- A complete route with stops, total distance, duration, and load tracking; supports incremental stop addition and dict serialization
- **`RoutingAlgorithm`** -- Abstract base class defining the `optimize()` interface for all routing algorithms
- **`NearestNeighborRouting`** -- Greedy nearest-neighbor heuristic that visits the closest unvisited location at each step
- **`TwoOptRouting`** -- 2-opt local search improvement algorithm that iteratively reverses route segments to reduce total distance
- **`DijkstraRouting`** -- Dijkstra's shortest path algorithm operating on a weighted graph with bidirectional edge support
- **`AStarRouting`** -- A* pathfinding algorithm using Euclidean distance heuristic for informed graph search
- **`create_routing_algorithm()`** -- Factory function to instantiate routing algorithms by name ("nearest_neighbor", "two_opt")

## Directory Contents

- `__init__.py` - All routing data structures and algorithm implementations (441 lines)
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.logistics.routing import Location, NearestNeighborRouting, DijkstraRouting

# Create locations
depot = Location(id="depot", name="Warehouse", latitude=46.2044, longitude=6.1432)
stop_a = Location(id="a", name="Customer A", latitude=46.5197, longitude=6.6323)

# Nearest neighbor routing
nn = NearestNeighborRouting()
route = nn.optimize([depot, stop_a], start=depot)

# Graph-based shortest path
dijkstra = DijkstraRouting()
dijkstra.add_edge("depot", "a", 35.0)
dijkstra.add_edge("a", "b", 20.0)
path, distance = dijkstra.shortest_path("depot", "b")
```

## Navigation

- **Parent Module**: [logistics](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
