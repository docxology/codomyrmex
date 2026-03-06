"""Heuristic routing algorithms (NearestNeighbor, 2-opt)."""

from abc import ABC, abstractmethod

from .models import Location, Route, RoutingConstraints


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


class NearestNeighborRouting(RoutingAlgorithm):
    """Simple nearest neighbor heuristic."""

    def optimize(
        self,
        locations: list[Location],
        start: Location,
        end: Location | None = None,
        constraints: RoutingConstraints | None = None,
    ) -> Route:
        route = Route(id="nn_route", stops=[])
        current = start
        remaining = {loc.id for loc in locations if loc.id != start.id}
        location_map = {loc.id: loc for loc in locations}
        route.add_stop(current, 0.0)
        while remaining:
            nearest = None
            nearest_dist = float("inf")
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
        if end and end.id != current.id:
            route.add_stop(end, current.distance_to(end))
        return route


class TwoOptRouting(RoutingAlgorithm):
    """2-opt improvement algorithm."""

    def __init__(self, max_iterations: int = 1000) -> None:
        self.max_iterations = max_iterations

    def _calculate_route_distance(self, route_order: list[Location]) -> float:
        total = 0.0
        for i in range(len(route_order) - 1):
            total += route_order[i].distance_to(route_order[i + 1])
        return total

    def _two_opt_swap(self, route: list[Location], i: int, j: int) -> list[Location]:
        return route[:i] + route[i : j + 1][::-1] + route[j + 1 :]

    def optimize(
        self,
        locations: list[Location],
        start: Location,
        end: Location | None = None,
        constraints: RoutingConstraints | None = None,
    ) -> Route:
        initial = NearestNeighborRouting().optimize(locations, start, end, constraints)
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
        result = Route(id="2opt_route", stops=[])
        prev = route_order[0]
        result.add_stop(prev, 0.0)
        for loc in route_order[1:]:
            dist = prev.distance_to(loc)
            result.add_stop(loc, dist)
            prev = loc
        return result
