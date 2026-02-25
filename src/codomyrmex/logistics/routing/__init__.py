"""
Logistics routing algorithms.

Provides implementations for vehicle routing and path optimization.
"""

import heapq
import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class Location:
    """A geographic location."""
    id: str
    name: str
    latitude: float
    longitude: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def distance_to(self, other: 'Location') -> float:
        """Calculate haversine distance to another location (in km)."""
        R = 6371  # Earth's radius in km

        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        return R * c


@dataclass
class RoutingConstraints:
    """Constraints for routing optimization."""
    max_distance: float | None = None  # km
    max_duration: float | None = None  # minutes
    max_stops: int | None = None
    required_stops: list[str] = field(default_factory=list)
    avoid_locations: list[str] = field(default_factory=list)
    vehicle_capacity: float | None = None
    time_windows: dict[str, tuple[int, int]] = field(default_factory=dict)


@dataclass
class RouteStop:
    """A stop in a route."""
    location: Location
    arrival_time: float | None = None
    departure_time: float | None = None
    service_time: float = 0.0
    load: float = 0.0


@dataclass
class Route:
    """A complete route."""
    id: str
    stops: list[RouteStop]
    total_distance: float = 0.0
    total_duration: float = 0.0
    total_load: float = 0.0

    def add_stop(
        self,
        location: Location,
        distance_from_prev: float,
        service_time: float = 0.0,
        load: float = 0.0,
        speed: float = 50.0,  # km/h
    ) -> None:
        """Add a stop to the route."""
        duration = (distance_from_prev / speed) * 60  # minutes

        arrival = 0.0
        if self.stops:
            prev = self.stops[-1]
            arrival = (prev.departure_time or 0) + duration

        stop = RouteStop(
            location=location,
            arrival_time=arrival,
            departure_time=arrival + service_time,
            service_time=service_time,
            load=load,
        )

        self.stops.append(stop)
        self.total_distance += distance_from_prev
        self.total_duration += duration + service_time
        self.total_load += load

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "id": self.id,
            "stops": [
                {
                    "location_id": s.location.id,
                    "location_name": s.location.name,
                    "arrival": s.arrival_time,
                    "departure": s.departure_time,
                }
                for s in self.stops
            ],
            "total_distance_km": round(self.total_distance, 2),
            "total_duration_min": round(self.total_duration, 2),
        }


class RoutingAlgorithm(ABC):
    """Abstract base class for routing algorithms."""

    @abstractmethod
    def optimize(
        self,
        locations: list[Location],
        start: Location,
        end: Location | None = None,
        constraints: RoutingConstraints | None = None,
    ) -> Route:
        """Optimize a route through the given locations."""
        pass


class NearestNeighborRouting(RoutingAlgorithm):
    """Simple nearest neighbor heuristic."""

    def optimize(
        self,
        locations: list[Location],
        start: Location,
        end: Location | None = None,
        constraints: RoutingConstraints | None = None,
    ) -> Route:
        """Execute Optimize operations natively."""
        route = Route(id="nn_route", stops=[])
        current = start
        remaining = set(loc.id for loc in locations if loc.id != start.id)
        location_map = {loc.id: loc for loc in locations}

        # Add start
        route.add_stop(current, 0.0)

        while remaining:
            # Find nearest unvisited
            nearest = None
            nearest_dist = float('inf')

            for loc_id in remaining:
                loc = location_map[loc_id]
                dist = current.distance_to(loc)
                if dist < nearest_dist:
                    nearest = loc
                    nearest_dist = dist

            if nearest:
                route.add_stop(nearest, nearest_dist)
                remaining.remove(nearest.id)
                current = nearest

        # Return to end if specified
        if end and end.id != current.id:
            dist = current.distance_to(end)
            route.add_stop(end, dist)

        return route


class TwoOptRouting(RoutingAlgorithm):
    """2-opt improvement algorithm."""

    def __init__(self, max_iterations: int = 1000):
        """Execute   Init   operations natively."""
        self.max_iterations = max_iterations

    def _calculate_route_distance(
        self,
        route_order: list[Location],
    ) -> float:
        """Calculate total route distance."""
        total = 0.0
        for i in range(len(route_order) - 1):
            total += route_order[i].distance_to(route_order[i + 1])
        return total

    def _two_opt_swap(
        self,
        route: list[Location],
        i: int,
        j: int,
    ) -> list[Location]:
        """Perform a 2-opt swap."""
        new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
        return new_route

    def optimize(
        self,
        locations: list[Location],
        start: Location,
        end: Location | None = None,
        constraints: RoutingConstraints | None = None,
    ) -> Route:
        """Execute Optimize operations natively."""
        # Initial route using nearest neighbor
        nn = NearestNeighborRouting()
        initial = nn.optimize(locations, start, end, constraints)

        # Extract location order
        route_order = [stop.location for stop in initial.stops]
        best_distance = self._calculate_route_distance(route_order)

        improved = True
        iterations = 0

        while improved and iterations < self.max_iterations:
            improved = False
            iterations += 1

            for i in range(1, len(route_order) - 2):
                for j in range(i + 1, len(route_order) - 1):
                    new_route = self._two_opt_swap(route_order, i, j)
                    new_distance = self._calculate_route_distance(new_route)

                    if new_distance < best_distance:
                        route_order = new_route
                        best_distance = new_distance
                        improved = True
                        break

                if improved:
                    break

        # Build final route
        result = Route(id="2opt_route", stops=[])
        prev = route_order[0]
        result.add_stop(prev, 0.0)

        for loc in route_order[1:]:
            dist = prev.distance_to(loc)
            result.add_stop(loc, dist)
            prev = loc

        return result


class DijkstraRouting:
    """Dijkstra's shortest path algorithm for graph-based routing."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self.graph: dict[str, dict[str, float]] = {}

    def add_edge(
        self,
        from_id: str,
        to_id: str,
        distance: float,
        bidirectional: bool = True,
    ) -> None:
        """Add an edge to the graph."""
        if from_id not in self.graph:
            self.graph[from_id] = {}
        self.graph[from_id][to_id] = distance

        if bidirectional:
            if to_id not in self.graph:
                self.graph[to_id] = {}
            self.graph[to_id][from_id] = distance

    def shortest_path(
        self,
        start_id: str,
        end_id: str,
    ) -> tuple[list[str], float]:
        """Find shortest path between two nodes."""
        if start_id not in self.graph:
            return [], float('inf')

        distances = {node: float('inf') for node in self.graph}
        distances[start_id] = 0
        previous = dict.fromkeys(self.graph)
        visited = set()

        heap = [(0, start_id)]

        while heap:
            current_dist, current = heapq.heappop(heap)

            if current in visited:
                continue

            visited.add(current)

            if current == end_id:
                break

            for neighbor, weight in self.graph.get(current, {}).items():
                if neighbor in visited:
                    continue

                new_dist = current_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    heapq.heappush(heap, (new_dist, neighbor))

        # Reconstruct path
        path = []
        current = end_id
        while current is not None:
            path.append(current)
            current = previous.get(current)

        path.reverse()

        if path[0] != start_id:
            return [], float('inf')

        return path, distances[end_id]


class AStarRouting:
    """A* pathfinding algorithm."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self.graph: dict[str, dict[str, float]] = {}
        self.positions: dict[str, tuple[float, float]] = {}

    def add_node(
        self,
        node_id: str,
        x: float,
        y: float,
    ) -> None:
        """Add a node with position."""
        self.positions[node_id] = (x, y)
        if node_id not in self.graph:
            self.graph[node_id] = {}

    def add_edge(
        self,
        from_id: str,
        to_id: str,
        cost: float | None = None,
    ) -> None:
        """Add an edge (cost defaults to Euclidean distance)."""
        if cost is None:
            x1, y1 = self.positions.get(from_id, (0, 0))
            x2, y2 = self.positions.get(to_id, (0, 0))
            cost = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        if from_id not in self.graph:
            self.graph[from_id] = {}
        self.graph[from_id][to_id] = cost

    def _heuristic(self, node_id: str, goal_id: str) -> float:
        """Heuristic function (Euclidean distance)."""
        if node_id not in self.positions or goal_id not in self.positions:
            return 0

        x1, y1 = self.positions[node_id]
        x2, y2 = self.positions[goal_id]
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def find_path(
        self,
        start_id: str,
        goal_id: str,
    ) -> tuple[list[str], float]:
        """Find optimal path using A*."""
        if start_id not in self.graph:
            return [], float('inf')

        open_set = [(0, start_id)]
        came_from: dict[str, str] = {}
        g_score = {start_id: 0}
        f_score = {start_id: self._heuristic(start_id, goal_id)}
        open_set_hash = {start_id}

        while open_set:
            _, current = heapq.heappop(open_set)
            open_set_hash.discard(current)

            if current == goal_id:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path, g_score.get(goal_id, float('inf'))

            for neighbor, cost in self.graph.get(current, {}).items():
                tentative_g = g_score.get(current, float('inf')) + cost

                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self._heuristic(neighbor, goal_id)
                    f_score[neighbor] = f

                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f, neighbor))
                        open_set_hash.add(neighbor)

        return [], float('inf')


def create_routing_algorithm(
    algorithm_type: str,
    **kwargs
) -> RoutingAlgorithm:
    """Factory function for routing algorithms."""
    algorithms = {
        "nearest_neighbor": NearestNeighborRouting,
        "two_opt": TwoOptRouting,
    }

    algo_class = algorithms.get(algorithm_type)
    if not algo_class:
        raise ValueError(f"Unknown algorithm: {algorithm_type}")

    return algo_class(**kwargs)


__all__ = [
    "Location",
    "RoutingConstraints",
    "RouteStop",
    "Route",
    "RoutingAlgorithm",
    "NearestNeighborRouting",
    "TwoOptRouting",
    "DijkstraRouting",
    "AStarRouting",
    "create_routing_algorithm",
]
